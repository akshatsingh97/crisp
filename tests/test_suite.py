"""Tests for the evaluation suite logic (no model calls). Run: python3 -m unittest discover tests"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))

import gates  # noqa: E402
import run_suite  # noqa: E402

GATES = json.loads((ROOT / "evals" / "gates.json").read_text())["gates"]


class GateEvaluation(unittest.TestCase):
    def test_pass_fail_and_skip(self):
        sample = [{"id": "X1", "suite": "content", "name": "a", "metric": "m", "op": "<=", "value": 1},
                  {"id": "X2", "suite": "tldr", "name": "b", "metric": "n", "op": ">=", "value": 1},
                  {"id": "X3", "suite": "all", "name": "c", "metric": "leaks", "op": "<=", "value": 0}]
        result = {r["id"]: r["status"] for r in gates.evaluate(sample, {"m": 2, "n": 1, "leaks": 0}, ["content"])}
        self.assertEqual(result, {"X1": "FAIL", "X2": "SKIP", "X3": "PASS"})

    def test_incomplete_data_never_passes(self):
        sample = [{"id": "X1", "suite": "content", "name": "a", "metric": "m", "op": "<=", "value": 1},
                  {"id": "X2", "suite": "all", "name": "b", "metric": "leaks", "op": "<=", "value": 0}]
        metrics = {"m": 0, "leaks": 0, "incomplete_suites": ["content"], "incomplete_generation": True}
        statuses = [r["status"] for r in gates.evaluate(sample, metrics, ["content"])]
        self.assertEqual(statuses, ["INCOMPLETE", "INCOMPLETE"])
        metrics["incomplete_generation"] = False  # a judge failed, but every answer exists
        statuses = [r["status"] for r in gates.evaluate(sample, metrics, ["content"])]
        self.assertEqual(statuses, ["INCOMPLETE", "PASS"])

    def test_missing_metric_is_skipped(self):
        sample = [{"id": "X1", "suite": "content", "name": "a", "metric": "m", "op": "<=", "value": 1}]
        self.assertEqual(gates.evaluate(sample, {}, ["content"])[0]["status"], "SKIP")

    def test_gates_file_is_valid(self):
        ids = [g["id"] for g in GATES]
        self.assertEqual(len(ids), len(set(ids)))
        for gate in GATES:
            self.assertIn(gate["op"], gates.OPS)
            self.assertIn(gate["suite"], run_suite.ALL_SUITES + ["all"])

    def test_suite_config_references_real_scenarios(self):
        scenarios = {s["id"] for s in json.loads((ROOT / "evals" / "scenarios.json").read_text())}
        cfg = json.loads((ROOT / "evals" / "suite.json").read_text())
        for sid in cfg["strict_scenarios"] + cfg["on_demand_scenarios"]:
            self.assertIn(sid, scenarios)
        categories = {s["category"] for s in json.loads((ROOT / "evals" / "scenarios.json").read_text())}
        self.assertTrue({"depth", "code", "safety", "doc"} <= categories)


class Helpers(unittest.TestCase):
    def test_tldr_format(self):
        good = "Rebuild native modules after the upgrade, or the app crashes.\n\n- Run `npm rebuild`.\n- Update `.nvmrc`."
        self.assertTrue(run_suite.tldr_format_ok(good))
        self.assertFalse(run_suite.tldr_format_ok(good + "\n- one\n- two"))
        self.assertFalse(run_suite.tldr_format_ok("First sentence here. Second sentence here.\n- a"))
        self.assertFalse(run_suite.tldr_format_ok(" ".join(["word"] * 25) + "."))

    def test_skill_loaded(self):
        self.assertTrue(run_suite.skill_loaded([{"name": "Skill", "input": {"skill": "crisp:crisp"}}]))
        self.assertTrue(run_suite.skill_loaded([{"name": "Read", "input": {"file_path": "/x/skills/crisp/SKILL.md"}}]))
        self.assertFalse(run_suite.skill_loaded([{"name": "Bash", "input": {"command": "ls"}}]))

    def test_python_blocks_compile(self):
        self.assertTrue(run_suite.python_blocks_compile("```python\ndef f():\n    return 1\n```"))
        self.assertFalse(run_suite.python_blocks_compile("```python\ndef f(:\n```"))
        self.assertFalse(run_suite.python_blocks_compile("No code here."))

    def test_meta_leak_pattern(self):
        self.assertTrue(run_suite.META_LEAK.search("I followed the Crisp rules."))
        self.assertFalse(run_suite.META_LEAK.search("Use CREATE INDEX CONCURRENTLY."))


class RunnerSetup(unittest.TestCase):
    def test_probe_can_run_during_init(self):
        """Regression: the probe ran before the run counter existed."""
        original = run_suite.Runner._run
        calls = []
        run_suite.Runner._run = lambda self, *a: (calls.append(self.counter), ("OK", []))[1]
        try:
            runner = run_suite.Runner(10, isolate=True)
            self.assertTrue(runner.isolated)
            self.assertEqual(calls, [0])
            runner.close()
        finally:
            run_suite.Runner._run = original


class FakeRunner:
    """Returns scripted judge verdicts, to test pairwise() without a model."""
    def __init__(self, verdicts):
        self.verdicts = list(verdicts)

    def judge(self, prompt):
        return self.verdicts.pop(0)


class Pairwise(unittest.TestCase):
    def test_both_orders_must_agree_for_a_win(self):
        # First call: X = baseline. Second call: X = candidate.
        agree = FakeRunner([{"more_useful": "Y", "only_in_x": [], "only_in_y": []},
                            {"more_useful": "X", "only_in_x": [], "only_in_y": []}])
        self.assertEqual(run_suite.pairwise(agree, "q", "base", "cand")["winner"], "candidate")
        disagree = FakeRunner([{"more_useful": "X", "only_in_x": [], "only_in_y": []},
                               {"more_useful": "X", "only_in_x": [], "only_in_y": []}])
        self.assertEqual(run_suite.pairwise(disagree, "q", "base", "cand")["winner"], "equal")

    def test_items_are_mapped_to_the_right_side_and_averaged(self):
        crit = {"item": "warning", "importance": "critical"}
        runner = FakeRunner([{"more_useful": "X", "only_in_x": [crit], "only_in_y": []},   # baseline has it
                             {"more_useful": "Y", "only_in_x": [], "only_in_y": [crit]}])  # baseline (Y) has it
        result = run_suite.pairwise(runner, "q", "base", "cand")
        self.assertEqual(result["winner"], "baseline")
        self.assertEqual(result["cut"]["critical"], 1.0)
        self.assertEqual(result["added"]["critical"], 0.0)


if __name__ == "__main__":
    unittest.main()
