#!/usr/bin/env python3
"""Crisp evaluation suite with pass/fail gates.

The suite runs Claude Code (`claude -p`) with no plugin (the baseline) and
with one or more Crisp versions (the candidates). Then it measures each
candidate against the gates in evals/gates.json.

Suites:
  content    18 scenarios (evals/scenarios.json) in answer mode. A blind judge
             compares each candidate answer with the baseline answer in BOTH
             orders and lists the useful information that only one has
             (critical, useful, minor). A second judge checks must-cover facts
             and accuracy. The Crisp checker measures readability.
  strict     6 scenarios with the strict level.
  on_demand  3 ordinary questions in on-demand mode. Crisp must not load.
  tldr       /crisp:tldr on 2 long texts: format and the critical caveat.
  clarify    /crisp:clarify on 2 texts: every source fact kept, no new facts.
  check      /crisp:check: only real rule IDs.
  creative   A poem request. Crisp must not make it worse.
Every candidate output is also scanned for mentions of Crisp or its rules.

Usage:
  python3 evals/run_suite.py                               # baseline vs this repo
  python3 evals/run_suite.py --candidate crisp-1.1.0=/path/to/old/crisp --candidate crisp=.
  python3 evals/run_suite.py --suites tldr,clarify,check --runs 1

Output: evals/results/<date>-suite/ with every answer, every judge verdict,
metrics.json, and SUITE.md (the scorecard). Exit code 1 if a gate fails.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import pathlib
import py_compile
import random
import re
import shutil
import statistics as st
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVALS = ROOT / "evals"
sys.path.insert(0, str(ROOT / "skills" / "crisp" / "scripts"))
sys.path.insert(0, str(EVALS))
import crisp_check  # noqa: E402
from gates import evaluate  # noqa: E402

ALL_SUITES = ["content", "strict", "on_demand", "tldr", "clarify", "check", "creative"]
VALID_RULES = ({f"A{i}" for i in range(1, 13)} | {f"B{i}" for i in range(1, 15)} | {f"C{i}" for i in range(1, 7)}
               | {f"E{i}" for i in range(1, 15)} | {f"F{i}" for i in range(1, 11)})
META_LEAK = re.compile(r"\bcrisp\b|session rules|ASD-STE|writing rules", re.I)

PAIR_PROMPT = """You are a strict, neutral reviewer. Two AI assistants answered the same request.
You do not know which tool wrote which answer.

REQUEST:
{prompt}

ANSWER X:
<<<
{x}
>>>

ANSWER Y:
<<<
{y}
>>>

List every piece of USEFUL information that one answer contains and the other does not.
Count facts, steps, warnings, caveats, commands, examples, and alternatives. Do not count
wording, style, formatting, or repetition. Rate each item:
- critical: without it, the reader can make a mistake, lose data, or fail to solve the problem
- useful: it helps the reader, but the reader can succeed without it
- minor: nice to have
Then decide which answer is more useful to the reader overall.
Reply with JSON only:
{{"only_in_x": [{{"item": "...", "importance": "critical|useful|minor"}}],
  "only_in_y": [{{"item": "...", "importance": "critical|useful|minor"}}],
  "more_useful": "X|Y|equal", "reason": "one sentence"}}"""

FACTS_PROMPT = """You are a strict reviewer. A developer asked the request below.

REQUEST:
{prompt}

ANSWER:
<<<
{answer}
>>>

FACTS A GOOD ANSWER MUST COVER (numbered):
{facts}

For each fact, decide if the answer states it or clearly implies it. Then score accuracy
from 1 to 10 (technically correct, with no misleading statement).
Reply with JSON only: {{"covered": [true, false, ...], "accuracy": 0}}"""

CAVEAT_PROMPT = """Does the SUMMARY below state this point, in any wording?
POINT: {point}

SUMMARY:
<<<
{text}
>>>
Reply with JSON only: {{"stated": true}} or {{"stated": false}}"""

CLARIFY_PROMPT = """You compare a SOURCE text with a REWRITE of it.

SOURCE:
<<<
{source}
>>>

REWRITE:
<<<
{rewrite}
>>>

FACTS FROM THE SOURCE (numbered):
{facts}

1. For each numbered fact, decide if the REWRITE keeps it.
2. List every claim in the REWRITE that is not word for word in the SOURCE, and classify each one:
   - "restated": the source states it, implies it, or it follows directly from source claims
   - "new": a real new fact, such as a new number, step, tool, risk, or recommendation
   Ignore definitions of terms, a bottom-line summary of the source, and notes that say a
   source claim is unclear.
Reply with JSON only: {{"kept": [true, false, ...], "claims": [{{"claim": "...", "kind": "restated|new"}}]}}"""

CREATIVE_PROMPT = """Two writers answered this request: {prompt}

POEM X:
<<<
{x}
>>>

POEM Y:
<<<
{y}
>>>

Which poem better fulfils the request (playful, natural voice, four lines)?
Reply with JSON only: {{"better": "X|Y|equal"}}"""


# ------------------------------------------------------------------ running Claude

class Runner:
    def __init__(self, timeout, isolate=True):
        self.timeout = timeout
        self.work = pathlib.Path(tempfile.mkdtemp(prefix="crisp-suite-"))
        self.counter = 0
        self.probe_error = ""
        self.isolated = isolate and self._probe()

    def _home(self, label):
        if not self.isolated:
            return None
        home = self.work / "home" / label
        home.mkdir(parents=True, exist_ok=True)
        return home

    def _probe(self):
        """Check up to three times that `claude -p` works with an empty HOME."""
        home = self.work / "probe"
        home.mkdir(parents=True, exist_ok=True)
        self.probe_error = ""
        for _ in range(3):
            try:
                text, _ = self._run("Reply with the word OK only.", None, {}, home, False)
                if "OK" in text.upper():
                    return True
                self.probe_error = f"unexpected reply: {text[:120]!r}"
            except Exception as error:  # noqa: BLE001
                self.probe_error = str(error)[:300]
        return False

    def _run(self, prompt, plugin_dir, env_extra, home, stream):
        cmd = ["claude", "-p", prompt]
        if plugin_dir:
            cmd += ["--plugin-dir", str(plugin_dir)]
        if stream:
            cmd += ["--output-format", "stream-json", "--verbose"]
        env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE_PLUGIN_OPTION_", "CRISP_"))}
        if home:
            env["HOME"] = str(home)
        env.update(env_extra)
        self.counter += 1
        cwd = self.work / "cwd" / str(self.counter)
        cwd.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=self.timeout)
        if result.returncode != 0:
            detail = (result.stderr.strip() or result.stdout.strip())[-300:]
            raise RuntimeError(f"claude exited {result.returncode}: {detail}")
        if not stream:
            return result.stdout.strip(), []
        text, tools = "", []
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "assistant":
                for part in event.get("message", {}).get("content", []):
                    if part.get("type") == "tool_use":
                        tools.append({"name": part.get("name"), "input": part.get("input")})
            if event.get("type") == "result":
                text = event.get("result", "")
        return text.strip(), tools

    def _retry(self, fn, attempts=4):
        """Run fn, retrying failed model calls with exponential backoff and jitter."""
        for attempt in range(1, attempts + 1):
            try:
                return fn()
            except Exception:  # noqa: BLE001
                if attempt == attempts:
                    raise
                time.sleep(min(60, 5 * 2 ** (attempt - 1)) * random.uniform(0.5, 1.5))

    def generate(self, label, prompt, plugin_dir=None, env_extra=None, stream=False):
        def call():
            text, tools = self._run(prompt, plugin_dir, env_extra or {}, self._home(label), stream)
            if not text.strip():
                raise RuntimeError("empty answer")
            return text, tools
        return self._retry(call)

    def judge(self, prompt):
        def call():
            text, _ = self._run(prompt, None, {}, self._home("judge"), False)
            match = re.search(r"\{.*\}", text, re.S)
            if not match:
                raise RuntimeError(f"judge returned no JSON: {text[:200]}")
            return json.loads(match.group(0))
        return self._retry(call)

    def close(self):
        shutil.rmtree(self.work, ignore_errors=True)


# ------------------------------------------------------------------ helpers

def words(text):
    """Every word in the output, code included, so a code-heavy answer is measured fairly."""
    return len((text or "").split())


def pairwise(runner, prompt, base, cand):
    """Judge a pair in both orders. Return averaged item counts and a debiased verdict."""
    first = runner.judge(PAIR_PROMPT.format(prompt=prompt, x=base, y=cand))   # X = baseline
    second = runner.judge(PAIR_PROMPT.format(prompt=prompt, x=cand, y=base))  # X = candidate
    verdicts = [{"X": "baseline", "Y": "candidate"}.get(first.get("more_useful"), "equal"),
                {"X": "candidate", "Y": "baseline"}.get(second.get("more_useful"), "equal")]
    winner = verdicts[0] if verdicts[0] == verdicts[1] else "equal"
    cut = first.get("only_in_x", []) + second.get("only_in_y", [])
    added = first.get("only_in_y", []) + second.get("only_in_x", [])

    def avg(items, level):
        return sum(1 for i in items if i.get("importance") == level) / 2

    return {"winner": winner, "verdicts": verdicts,
            "cut": {lvl: avg(cut, lvl) for lvl in ("critical", "useful", "minor")},
            "added": {lvl: avg(added, lvl) for lvl in ("critical", "useful", "minor")},
            "cut_items": cut, "added_items": added}


def facts_judge(runner, scenario, answer):
    facts = "\n".join(f"{n}. {f}" for n, f in enumerate(scenario["must_cover"], 1))
    data = runner.judge(FACTS_PROMPT.format(prompt=scenario["prompt"], answer=answer, facts=facts))
    covered = [bool(x) for x in data.get("covered", [])][:len(scenario["must_cover"])]
    covered += [False] * (len(scenario["must_cover"]) - len(covered))
    return {"coverage": sum(covered) / len(covered), "accuracy": data.get("accuracy")}


def python_blocks_compile(text):
    blocks = re.findall(r"```(?:python|py)\n(.*?)```", text, re.S)
    if not blocks:
        return False
    for block in blocks:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
            fh.write(block)
        try:
            py_compile.compile(fh.name, doraise=True)
        except py_compile.PyCompileError:
            return False
        finally:
            os.unlink(fh.name)
    return True


def tldr_format_ok(text):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    bullets = [l for l in lines if re.match(r"^([-*+]|\d+[.)])\s", l)]
    head = [l for l in lines if l not in bullets]
    if len(head) != 1 or len(bullets) > 3:
        return False
    report = crisp_check.check(head[0])
    return report["sentences"] == 1 and report["words"] <= 20


def skill_loaded(tools):
    for tool in tools:
        blob = json.dumps(tool.get("input") or {}).lower()
        if tool.get("name") == "Skill" and "crisp" in blob:
            return True
        if tool.get("name") == "Read" and "skills/crisp" in blob:
            return True
    return False


def mean(values, default=None):
    values = [v for v in values if isinstance(v, (int, float))]
    return st.mean(values) if values else default


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", action="append", default=[], help="NAME=PATH of a Crisp plugin directory.")
    ap.add_argument("--suites", default=",".join(ALL_SUITES))
    ap.add_argument("--runs", type=int, default=2, help="Runs per content scenario.")
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="")
    ap.add_argument("--no-isolate", action="store_true")
    ap.add_argument("--only", default="", help="Comma-separated content scenario ids (for a quick run).")
    ap.add_argument("--resume", action="store_true",
                    help="Reuse answers and verdicts already saved in --out, and run only what is missing.")
    args = ap.parse_args()

    if not shutil.which("claude"):
        sys.exit("The claude CLI is not on PATH.")
    candidates = []
    for spec in args.candidate or ["crisp=" + str(ROOT)]:
        name, path = spec.split("=", 1)
        path = pathlib.Path(path).expanduser().resolve()
        if not (path / ".claude-plugin" / "plugin.json").is_file():
            sys.exit(f"not a plugin directory: {path}")
        candidates.append((name, path))
    suites = [s for s in args.suites.split(",") if s]
    scenarios = json.loads((EVALS / "scenarios.json").read_text())
    by_id = {s["id"]: s for s in scenarios}
    if args.only:
        wanted = set(args.only.split(","))
        scenarios = [s for s in scenarios if s["id"] in wanted]
    suite_cfg = json.loads((EVALS / "suite.json").read_text())
    gates = json.loads((EVALS / "gates.json").read_text())["gates"]
    out = pathlib.Path(args.out) if args.out else EVALS / "results" / f"{dt.date.today().isoformat()}-suite"
    out.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)

    runner = Runner(args.timeout, isolate=not args.no_isolate)
    if not runner.isolated and not args.no_isolate:
        runner.close()
        sys.exit("Isolation failed: claude -p does not work with an empty HOME "
                 f"({runner.probe_error}). Set ANTHROPIC_API_KEY, or rerun with --no-isolate after you "
                 "disable your installed copy of Crisp.")
    pool = cf.ThreadPoolExecutor(args.jobs)
    log = []

    def save(rel, data):
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data if isinstance(data, str) else json.dumps(data, indent=1), encoding="utf-8")

    def safe(fn, *a):
        try:
            return fn(*a)
        except Exception as error:  # noqa: BLE001
            log.append(str(error)[:300])
            return None

    # ---- generation
    gen_jobs = {}

    def answer_path(key):
        return out / f"answers/{key[0]}/{key[1]}/{key[2]}-run{key[3]}.md"

    def add_gen(key, label, prompt, plugin=None, env=None, stream=False):
        path, tools_path = answer_path(key), answer_path(key).with_suffix(".tools.json")
        if args.resume and path.is_file() and path.read_text().strip() and (not stream or tools_path.is_file()):
            saved = (path.read_text().strip(), json.loads(tools_path.read_text()) if stream else [])
            gen_jobs[key] = pool.submit(lambda v=saved: v)
            return
        gen_jobs[key] = pool.submit(safe, runner.generate, label, prompt, plugin, env, stream)

    runs = range(1, args.runs + 1)
    if "content" in suites or "strict" in suites:
        for s in scenarios:
            for r in runs:
                add_gen(("none", "content", s["id"], r), "none", s["prompt"])
                for name, path in candidates:
                    add_gen((name, "content", s["id"], r), name, s["prompt"], path)
    if "strict" in suites:
        for sid in suite_cfg["strict_scenarios"]:
            for name, path in candidates:
                add_gen((name, "strict", sid, 1), name + "-strict", by_id[sid]["prompt"], path, {"CRISP_LEVEL": "strict"})
    if "on_demand" in suites:
        for sid in suite_cfg["on_demand_scenarios"]:
            for name, path in candidates:
                add_gen((name, "on_demand", sid, 1), name + "-ondemand", by_id[sid]["prompt"], path,
                        {"CRISP_MODE": "on-demand"}, True)
    for kind, command in (("tldr", "/crisp:tldr"), ("clarify", "/crisp:clarify"), ("check", "/crisp:check")):
        if kind in suites:
            for case in suite_cfg[kind]:
                for name, path in candidates:
                    add_gen((name, kind, case["id"], 1), name, f"{command} {case['text']}", path)
    if "creative" in suites:
        for case in suite_cfg["creative"]:
            add_gen(("none", "creative", case["id"], 1), "none", case["prompt"])
            for name, path in candidates:
                add_gen((name, "creative", case["id"], 1), name, case["prompt"], path)

    gens, missing_gen = {}, set()
    for key, future in gen_jobs.items():
        result = future.result()
        if not result:
            missing_gen.add(key)
        gens[key] = result if result else ("", [])
        if result:
            save(f"answers/{key[0]}/{key[1]}/{key[2]}-run{key[3]}.md", gens[key][0] + "\n")
            if key[1] == "on_demand":
                save(f"answers/{key[0]}/{key[1]}/{key[2]}-run{key[3]}.tools.json", gens[key][1])
    print(f"generated {len(gens)} outputs", flush=True)

    def text(key):
        return gens.get(key, ("", []))[0]

    # ---- judging
    judge_jobs = {}

    def submit_judge(key, *call):
        """Reuse a saved verdict when --resume is set; otherwise call the judge."""
        path = out / f"judge/{key[1]}/{key[2]}/{key[0]}-{key[3]}-run{key[4]}.json"
        if args.resume and path.is_file():
            saved = json.loads(path.read_text())
            if saved:
                judge_jobs[key] = pool.submit(lambda v=saved: v)
                return
        judge_jobs[key] = pool.submit(*call)
    if "content" in suites or "strict" in suites:
        for s in scenarios:
            for r in runs:
                submit_judge(("facts", "none", "content", s["id"], r), 
                    safe, facts_judge, runner, s, text(("none", "content", s["id"], r)))
    for name, _ in candidates:
        if "content" in suites:
            for s in scenarios:
                for r in runs:
                    cand = text((name, "content", s["id"], r))
                    submit_judge(("facts", name, "content", s["id"], r), safe, facts_judge, runner, s, cand)
                    submit_judge(("pair", name, "content", s["id"], r), 
                        safe, pairwise, runner, s["prompt"], text(("none", "content", s["id"], r)), cand)
        if "strict" in suites:
            for sid in suite_cfg["strict_scenarios"]:
                submit_judge(("facts", name, "strict", sid, 1), 
                    safe, facts_judge, runner, by_id[sid], text((name, "strict", sid, 1)))
        if "tldr" in suites:
            for case in suite_cfg["tldr"]:
                submit_judge(("caveat", name, "tldr", case["id"], 1), 
                    safe, runner.judge, CAVEAT_PROMPT.format(point=case["critical"], text=text((name, "tldr", case["id"], 1))))
        if "clarify" in suites:
            for case in suite_cfg["clarify"]:
                facts = "\n".join(f"{n}. {f}" for n, f in enumerate(case["facts"], 1))
                submit_judge(("clarify", name, "clarify", case["id"], 1), 
                    safe, runner.judge, CLARIFY_PROMPT.format(source=case["text"], rewrite=text((name, "clarify", case["id"], 1)), facts=facts))
        if "creative" in suites:
            for case in suite_cfg["creative"]:
                base, cand = text(("none", "creative", case["id"], 1)), text((name, "creative", case["id"], 1))
                submit_judge(("creative", name, "creative", case["id"], 1), 
                    lambda b=base, c=cand, p=case["prompt"]: [
                        safe(runner.judge, CREATIVE_PROMPT.format(prompt=p, x=b, y=c)),
                        safe(runner.judge, CREATIVE_PROMPT.format(prompt=p, x=c, y=b))])
    judged, missing_judge = {}, set()
    for key, future in judge_jobs.items():
        judged[key] = future.result()
        bad = not judged[key] or (isinstance(judged[key], list) and not all(judged[key]))
        if bad:
            missing_judge.add(key)
        else:
            save(f"judge/{key[1]}/{key[2]}/{key[0]}-{key[3]}-run{key[4]}.json", judged[key])
    print(f"judged {len(judged)} items", flush=True)
    pool.shutdown()

    # ---- metrics
    metrics = {}
    base_facts = {k[3:]: v for k, v in judged.items() if k[0] == "facts" and k[1] == "none" and v}
    base_words = {(s["id"], r): words(text(("none", "content", s["id"], r))) for s in scenarios for r in runs}
    for name, _ in candidates:
        m = {}
        incomplete = set()
        for key in missing_gen:
            if key[0] in (name, "none"):
                incomplete.add("content" if key[1] == "content" else key[1])
        for key in missing_judge:
            if key[1] in (name, "none"):
                incomplete.add(key[2])
        if "content" in incomplete and "strict" in suites:
            incomplete.add("strict")
        m["incomplete_suites"] = sorted(incomplete)
        m["incomplete_generation"] = any(k[0] in (name, "none") for k in missing_gen)
        m["missing_calls"] = sum(1 for k in missing_gen if k[0] in (name, "none")) + \
            sum(1 for k in missing_judge if k[1] in (name, "none"))
        leaks = 0
        for key, (out_text, _) in gens.items():
            if key[0] == name and key[1] not in ("check",) and META_LEAK.search(out_text or ""):
                leaks += 1
        m["meta_leaks"] = leaks
        if "content" in suites:
            pairs = [judged.get(("pair", name, "content", s["id"], r)) for s in scenarios for r in runs]
            pairs = [p for p in pairs if p]
            n = max(1, len(pairs))
            crit_cut = sum(p["cut"]["critical"] for p in pairs)
            crit_add = sum(p["added"]["critical"] for p in pairs)
            use_cut = sum(p["cut"]["useful"] for p in pairs)
            use_add = sum(p["added"]["useful"] for p in pairs)
            wins = sum(p["winner"] == "candidate" for p in pairs)
            losses = sum(p["winner"] == "baseline" for p in pairs)
            ties = len(pairs) - wins - losses
            m.update({
                "pairs": len(pairs), "wins": wins, "losses": losses, "ties": ties,
                "critical_cut_per_pair": round(crit_cut / n, 3),
                "critical_added_per_pair": round(crit_add / n, 3),
                "critical_cut_minus_added_per_pair": round((crit_cut - crit_add) / n, 3),
                "useful_cut_per_pair": round(use_cut / n, 2), "useful_added_per_pair": round(use_add / n, 2),
                "useful_cut_to_added_ratio": round(use_cut / use_add, 2) if use_add else (0.0 if not use_cut else 99.0),
                "preference_margin": round((wins + ties / 2 - losses) / n, 3),
            })
            cand_facts = [judged.get(("facts", name, "content", s["id"], r)) for s in scenarios for r in runs]
            m["coverage_delta_pts"] = round(100 * (mean([f["coverage"] for f in cand_facts if f], 0)
                                                   - mean([f["coverage"] for f in base_facts.values()], 0)), 1)
            m["accuracy_delta"] = round(mean([f["accuracy"] for f in cand_facts if f], 0)
                                        - mean([f["accuracy"] for f in base_facts.values()], 0), 2)
            reports = [crisp_check.check(text((name, "content", s["id"], r)), text_type=s["type"])
                       for s in scenarios for r in runs]
            m["candidate_checker_score"] = round(mean([rep["score"] for rep in reports], 0), 1)
            m["candidate_over_limit_per_answer"] = round(mean(
                [sum(1 for i in rep["issues"] if i["rule"] == "B1") for rep in reports], 0), 2)
            cand_words = [words(text((name, "content", s["id"], r))) for s in scenarios for r in runs]
            m["length_ratio"] = round(sum(cand_words) / max(1, sum(base_words.values())), 3)
            depth = [(words(text((name, "content", s["id"], r))), base_words[(s["id"], r)])
                     for s in scenarios if s["category"] == "depth" for r in runs]
            m["depth_length_ratio"] = round(sum(c for c, _ in depth) / max(1, sum(b for _, b in depth)), 3) if depth else None
            code = [python_blocks_compile(text((name, "content", s["id"], r)))
                    for s in scenarios if s["category"] == "code" for r in runs]
            m["code_compile_rate"] = round(sum(code) / len(code), 3) if code else None
            per_cat = {}
            for s in scenarios:
                for r in runs:
                    p = judged.get(("pair", name, "content", s["id"], r))
                    if p:
                        c = per_cat.setdefault(s["category"], {"pairs": 0, "wins": 0, "losses": 0, "critical_cut": 0.0,
                                                                "useful_cut": 0.0, "useful_added": 0.0})
                        c["pairs"] += 1
                        c["wins"] += p["winner"] == "candidate"
                        c["losses"] += p["winner"] == "baseline"
                        c["critical_cut"] += p["cut"]["critical"]
                        c["useful_cut"] += p["cut"]["useful"]
                        c["useful_added"] += p["added"]["useful"]
            m["by_category"] = per_cat
            m["critical_cut_examples"] = [f"{s['id']}-run{r}: {i['item']}" for s in scenarios for r in runs
                                          for i in (judged.get(("pair", name, "content", s["id"], r)) or {}).get("cut_items", [])
                                          if i.get("importance") == "critical"]
        if "strict" in suites:
            ids = suite_cfg["strict_scenarios"]
            strict_f = [judged.get(("facts", name, "strict", sid, 1)) for sid in ids]
            base_f = [base_facts.get(("content", sid, 1)) for sid in ids]
            m["strict_coverage_delta_pts"] = round(100 * (mean([f["coverage"] for f in strict_f if f], 0)
                                                          - mean([f["coverage"] for f in base_f if f], 0)), 1)
            strict_score = mean([crisp_check.check(text((name, "strict", sid, 1)), text_type=by_id[sid]["type"])["score"] for sid in ids], 0)
            lite_score = mean([crisp_check.check(text((name, "content", sid, 1)), text_type=by_id[sid]["type"])["score"] for sid in ids], 0)
            m["strict_minus_lite_checker"] = round(strict_score - lite_score, 1)
        if "on_demand" in suites:
            m["on_demand_skill_loads"] = sum(skill_loaded(gens.get((name, "on_demand", sid, 1), ("", []))[1])
                                             for sid in suite_cfg["on_demand_scenarios"])
        if "tldr" in suites:
            cases = suite_cfg["tldr"]
            m["tldr_format_rate"] = round(sum(tldr_format_ok(text((name, "tldr", c["id"], 1))) for c in cases) / len(cases), 3)
            m["tldr_caveat_rate"] = round(sum(bool((judged.get(("caveat", name, "tldr", c["id"], 1)) or {}).get("stated"))
                                              for c in cases) / len(cases), 3)
        if "clarify" in suites:
            cases = suite_cfg["clarify"]
            kept, total, added = 0, 0, 0
            for c in cases:
                verdict = judged.get(("clarify", name, "clarify", c["id"], 1)) or {}
                flags = [bool(x) for x in verdict.get("kept", [])][:len(c["facts"])]
                kept += sum(flags)
                total += len(c["facts"])
                added += sum(1 for c in verdict.get("claims", []) or [] if c.get("kind") == "new")
            m["clarify_fact_rate"] = round(kept / max(1, total), 3)
            m["clarify_added_facts"] = added
            m["clarify_format_rate"] = round(sum(text((name, "clarify", c["id"], 1)).lstrip("*# ").lower().startswith("bottom line")
                                                 for c in cases) / len(cases), 3)
        if "check" in suites:
            invalid = set()
            for c in suite_cfg["check"]:
                for rule in re.findall(r"\b([A-F]\d{1,2})\b", text((name, "check", c["id"], 1))):
                    if rule not in VALID_RULES:
                        invalid.add(rule)
            m["check_invalid_rule_ids"] = len(invalid)
            m["check_invalid_examples"] = sorted(invalid)
        if "creative" in suites:
            ok = []
            for c in suite_cfg["creative"]:
                pair = judged.get(("creative", name, "creative", c["id"], 1)) or [None, None]
                v1 = {"X": "baseline", "Y": "candidate"}.get((pair[0] or {}).get("better"), "equal")
                v2 = {"X": "candidate", "Y": "baseline"}.get((pair[1] or {}).get("better"), "equal")
                ok.append(not (v1 == "baseline" and v2 == "baseline"))
            m["creative_not_worse_rate"] = round(sum(ok) / len(ok), 3)
        metrics[name] = m

    results = {name: evaluate(gates, metrics[name], suites) for name, _ in candidates}
    meta = {"date": dt.date.today().isoformat(), "runs": args.runs, "isolated": runner.isolated,
            "claude_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
            "suites": suites, "candidates": [n for n, _ in candidates], "errors": log}
    save("metrics.json", {"meta": meta, "metrics": metrics, "gates": results})
    save("SUITE.md", render(meta, gates, metrics, results, candidates))
    runner.close()
    print((out / "SUITE.md").read_text())
    return 1 if any(g["status"] in ("FAIL", "INCOMPLETE") for r in results.values() for g in r) else 0


def fmt(value):
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".") if abs(value) < 100 else f"{value:.0f}"
    return str(value)


def render(meta, gates, metrics, results, candidates):
    names = [n for n, _ in candidates]
    lines = [f"# Crisp evaluation suite, {meta['date']}", "",
             f"- Claude Code: {meta['claude_version']}", f"- Runs per content scenario: {meta['runs']}",
             f"- Isolated HOME: {'yes' if meta['isolated'] else 'no'}",
             f"- Suites: {', '.join(meta['suites'])}",
             "- Baseline: Claude Code with no plugin. Pairwise verdicts come from a blind judge that sees each pair in both orders. A pair counts as a win or a loss only if both orders agree.",
             "", "## Gates", "",
             "| Gate | Check | Target | " + " | ".join(names) + " |",
             "|---|---|---|" + "---|" * len(names)]
    for gate in gates:
        cells = []
        for name in names:
            res = next((g for g in results[name] if g["id"] == gate["id"]), None)
            if not res or res["status"] == "SKIP":
                cells.append("skipped")
            else:
                label = {"PASS": "PASS", "FAIL": "**FAIL**", "INCOMPLETE": "**INCOMPLETE**"}[res["status"]]
                cells.append(f"{label} ({fmt(res['value'])})")
        lines.append(f"| {gate['id']} | {gate['name']} | {gate['op']} {fmt(gate['value'])} | " + " | ".join(cells) + " |")
    for name in names:
        m = metrics[name]
        passed = sum(g["status"] == "PASS" for g in results[name])
        failed = sum(g["status"] in ("FAIL", "INCOMPLETE") for g in results[name])
        lines += ["", f"## {name}: {passed} passed, {failed} failed or incomplete", ""]
        if m.get("incomplete_suites"):
            lines += [f"- Incomplete data in: {', '.join(m['incomplete_suites'])} ({m['missing_calls']} failed model calls). "
                      "Rerun with --resume to fill the gaps.", ""]
        if "pairs" in m:
            lines += [f"- Pairwise vs no plugin: {m['wins']} wins, {m['losses']} losses, {m['ties']} ties (of {m['pairs']}).",
                      f"- Per pair: critical items cut {fmt(m['critical_cut_per_pair'])}, added {fmt(m['critical_added_per_pair'])}. "
                      f"Useful items cut {fmt(m['useful_cut_per_pair'])}, added {fmt(m['useful_added_per_pair'])}.",
                      f"- Length vs no plugin: {fmt(m['length_ratio'])}x. Readability score: {fmt(m['candidate_checker_score'])}.",
                      "", "| Category | Pairs | Wins | Losses | Critical cut | Useful cut | Useful added |", "|---|---|---|---|---|---|---|"]
            for cat, c in sorted(m["by_category"].items()):
                lines.append(f"| {cat} | {c['pairs']} | {c['wins']} | {c['losses']} | {fmt(c['critical_cut'])} | "
                             f"{fmt(c['useful_cut'])} | {fmt(c['useful_added'])} |")
            if m["critical_cut_examples"]:
                lines += ["", "Critical items that this version cut (as listed by the judge):", ""]
                lines += [f"- {e}" for e in m["critical_cut_examples"][:20]]
    if meta["errors"]:
        lines += ["", "## Errors", ""] + [f"- {e}" for e in meta["errors"][:20]]
    lines += ["", "## Limits", "",
              "- The judge is a Claude model that judges Claude text. Family bias is possible.",
              "- Each run samples the model, so numbers move between runs. Small differences are noise.",
              "- The readability gates use Crisp's own checker. The content gates do not.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
