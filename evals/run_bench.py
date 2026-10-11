#!/usr/bin/env python3
"""Crisp benchmark: compare answers with and without a writing plugin.

For each scenario in evals/scenarios.json and each condition, the script asks
Claude Code (`claude -p`) the same prompt. Then it scores each answer two ways:

1. The Crisp checker: readability score, words, longest sentence.
2. A blind judge (a separate `claude -p` run with no plugins). The judge sees
   the question, the answer, and the list of facts that a good answer must
   cover. It does not know which plugin wrote the answer. It marks each fact
   as covered or not, and scores accuracy, clarity, and scan speed from 1 to 10.

Usage:
    python3 evals/run_bench.py                                  # none vs crisp
    python3 evals/run_bench.py --conditions none,crisp,simple-english=../SimpleEnglish
    python3 evals/run_bench.py --only charge-retry,pg-index --runs 2

Conditions:
    none          Claude Code with no plugin
    crisp         this repository, loaded with --plugin-dir
    NAME=PATH     any other plugin directory, loaded with --plugin-dir

Isolation: the script first tests whether `claude -p` works with an empty
HOME (for example, with ANTHROPIC_API_KEY set). If it does, every run uses an
empty HOME, so your own plugins and settings cannot change the result. If it
does not, the runs use your normal HOME. Then disable your own copy of Crisp
before you run the benchmark. Use --no-isolate to skip the test.

Output: evals/results/<date>/ with answers/, judge/, results.json, RESULTS.md.
Python 3.8+, standard library only. Needs the `claude` CLI.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import statistics as st
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "crisp" / "scripts"))
import crisp_check  # noqa: E402

JUDGE_PROMPT = """You are a strict, neutral reviewer. A developer asked an AI assistant the request below.
Judge the answer from the reader's side. You do not know which tool wrote it.

REQUEST:
{prompt}

ANSWER:
<<<
{answer}
>>>

FACTS A GOOD ANSWER MUST COVER (numbered):
{facts}

For each fact, decide if the answer states it or clearly implies it. Then score from 1 to 10:
- accuracy: technically correct, with no misleading statement
- clarity: easy to understand on one read
- scan: the reader finds what to do fast

Reply with JSON only, no other text:
{{"covered": [true, false, ...], "accuracy": 0, "clarity": 0, "scan": 0, "errors": ["each wrong or misleading statement, or empty"]}}"""


def parse_conditions(spec):
    conditions = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        if item == "none":
            conditions.append(("none", None))
        elif item == "crisp":
            conditions.append(("crisp", ROOT))
        elif "=" in item:
            name, path = item.split("=", 1)
            path = pathlib.Path(path).expanduser().resolve()
            if not path.is_dir():
                sys.exit(f"plugin directory not found: {path}")
            conditions.append((name.strip(), path))
        else:
            sys.exit(f"unknown condition {item!r}. Use none, crisp, or NAME=PATH.")
    return conditions


def can_isolate(work, timeout):
    """Return True if `claude -p` works with an empty HOME (so the login does not depend on HOME)."""
    home = work / "probe-home"
    home.mkdir(parents=True, exist_ok=True)
    try:
        answer = run_claude("Reply with the word OK only.", None, home, work, timeout)
    except Exception:  # noqa: BLE001
        return False
    return "OK" in answer.upper()


def run_claude(prompt, plugin_dir, home, cwd, timeout):
    cmd = ["claude", "-p", prompt]
    if plugin_dir:
        cmd += ["--plugin-dir", str(plugin_dir)]
    env = dict(os.environ)
    if home:
        env["HOME"] = str(home)
    for key in [k for k in env if k.startswith(("CLAUDE_PLUGIN_OPTION_", "CRISP_"))]:
        del env[key]
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()[:300]}")
    return result.stdout.strip()


def judge(scenario, answer, home, cwd, timeout):
    facts = "\n".join(f"{n}. {f}" for n, f in enumerate(scenario["must_cover"], 1))
    raw = run_claude(JUDGE_PROMPT.format(prompt=scenario["prompt"], answer=answer, facts=facts),
                     None, home, cwd, timeout)
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        raise RuntimeError(f"judge returned no JSON: {raw[:200]}")
    data = json.loads(match.group(0))
    covered = [bool(x) for x in data.get("covered", [])][:len(scenario["must_cover"])]
    covered += [False] * (len(scenario["must_cover"]) - len(covered))
    return {"covered": covered, "coverage": sum(covered) / len(covered),
            "accuracy": data.get("accuracy"), "clarity": data.get("clarity"), "scan": data.get("scan"),
            "errors": data.get("errors") or []}


def checker_metrics(answer, text_type):
    report = crisp_check.check(answer, text_type=text_type)
    limit_issues = sum(1 for i in report["issues"] if i["rule"] == "B1")
    return {"crisp_score": report["score"], "words": report["words"],
            "longest_sentence": report["longest_sentence_words"], "sentences_over_limit": limit_issues}


def mean(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return round(st.mean(values), 2) if values else None


def write_report(out, conditions, scenarios, rows, meta):
    lines = [f"# Crisp benchmark, {meta['date']}", "",
             f"- Scenarios: {len(scenarios)} ({sum(s['type'] == 'reply' for s in scenarios)} questions, "
             f"{sum(s['type'] == 'doc' for s in scenarios)} document tasks)",
             f"- Runs per scenario: {meta['runs']}",
             f"- Claude Code: {meta['claude_version']}",
             f"- Isolated HOME: {'yes' if meta['isolated'] else 'no'}",
             "- Judge: a separate `claude -p` run with no plugins. It does not see the condition name.",
             "", "## Summary", "",
             "| Measure | " + " | ".join(name for name, _ in conditions) + " |",
             "|---|" + "---|" * len(conditions)]
    measures = [
        ("Fact coverage (judge, %)", lambda r: r["judge"]["coverage"] * 100 if r.get("judge") else None),
        ("Accuracy (judge, 1-10)", lambda r: r["judge"]["accuracy"] if r.get("judge") else None),
        ("Clarity (judge, 1-10)", lambda r: r["judge"]["clarity"] if r.get("judge") else None),
        ("Scan speed (judge, 1-10)", lambda r: r["judge"]["scan"] if r.get("judge") else None),
        ("Crisp checker score (/100)", lambda r: r["metrics"]["crisp_score"]),
        ("Words per answer", lambda r: r["metrics"]["words"]),
        ("Longest sentence (words)", lambda r: r["metrics"]["longest_sentence"]),
        ("Sentences over the limit (per answer)", lambda r: r["metrics"]["sentences_over_limit"]),
    ]
    summary = {}
    for label, fn in measures:
        cells = []
        for name, _ in conditions:
            value = mean([fn(r) for r in rows if r["condition"] == name])
            summary.setdefault(name, {})[label] = value
            cells.append("-" if value is None else (f"{value:.0f}" if "%" in label or "Words" in label
                                                      or "/100" in label else f"{value:.1f}"))
        lines.append(f"| {label} | " + " | ".join(cells) + " |")

    lines += ["", "## Fact coverage per scenario (covered / total)", "",
              "| Scenario | Type | " + " | ".join(name for name, _ in conditions) + " |",
              "|---|---|" + "---|" * len(conditions)]
    for s in scenarios:
        cells = []
        for name, _ in conditions:
            hits = [r for r in rows if r["condition"] == name and r["id"] == s["id"] and r.get("judge")]
            cells.append(" / ".join(f"{sum(r['judge']['covered'])}/{len(s['must_cover'])}" for r in hits) or "-")
        lines.append(f"| {s['id']} | {s['type']} | " + " | ".join(cells) + " |")

    errors = [(r["condition"], r["id"], e) for r in rows if r.get("judge") for e in r["judge"]["errors"] if e]
    if errors:
        lines += ["", "## Errors the judge found", ""]
        lines += [f"- {cond} / {sid}: {err}" for cond, sid, err in errors]
    failed = [r for r in rows if r.get("error")]
    if failed:
        lines += ["", "## Failed runs", ""] + [f"- {r['condition']} / {r['id']}: {r['error']}" for r in failed]
    lines += ["", "## Limits", "",
              "- The judge is a Claude model that judges Claude text. Family bias is possible.",
              "- Small samples move between runs. Run with `--runs 3` before you trust a difference of a few points.",
              "- The checker measures Crisp's own rules, so it favors Crisp. The judge scores do not use the checker.", ""]
    (out / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenarios", default=str(ROOT / "evals" / "scenarios.json"))
    ap.add_argument("--conditions", default="none,crisp")
    ap.add_argument("--only", default="", help="Comma-separated scenario ids.")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--no-isolate", action="store_true", help="Use your normal HOME for every run.")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    if not shutil.which("claude"):
        sys.exit("The claude CLI is not on PATH.")
    scenarios = json.loads(pathlib.Path(args.scenarios).read_text())
    if args.only:
        wanted = set(args.only.split(","))
        scenarios = [s for s in scenarios if s["id"] in wanted]
    conditions = parse_conditions(args.conditions)
    date = dt.date.today().isoformat()
    out = pathlib.Path(args.out) if args.out else ROOT / "evals" / "results" / date
    (out / "answers").mkdir(parents=True, exist_ok=True)
    (out / "judge").mkdir(parents=True, exist_ok=True)

    work = pathlib.Path(tempfile.mkdtemp(prefix="crisp-bench-"))
    isolated = False if args.no_isolate else can_isolate(work, args.timeout)
    if not isolated:
        print("Note: the runs use your normal HOME, so your installed plugins can change the result. "
              "Disable your installed copy of Crisp first.", file=sys.stderr)
    homes = {}
    for name in [c[0] for c in conditions] + ["judge"]:
        homes[name] = (work / "home" / name) if isolated else None
        if homes[name]:
            homes[name].mkdir(parents=True, exist_ok=True)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()

    jobs = [(s, name, path, run) for s in scenarios for name, path in conditions for run in range(1, args.runs + 1)]

    def one(job):
        s, name, path, run = job
        tag = f"{name}/{s['id']}" + (f"-run{run}" if args.runs > 1 else "")
        cwd = work / "cwd" / tag.replace("/", "_")
        cwd.mkdir(parents=True, exist_ok=True)
        row = {"condition": name, "id": s["id"], "type": s["type"], "run": run}
        try:
            answer = run_claude(s["prompt"], path, homes[name], cwd, args.timeout)
            (out / "answers" / name).mkdir(parents=True, exist_ok=True)
            (out / "answers" / f"{tag}.md").write_text(answer + "\n", encoding="utf-8")
            row["metrics"] = checker_metrics(answer, s["type"])
            if not args.no_judge:
                row["judge"] = judge(s, answer, homes["judge"], cwd, args.timeout)
                (out / "judge" / name).mkdir(parents=True, exist_ok=True)
                (out / "judge" / f"{tag}.json").write_text(json.dumps(row["judge"], indent=1), encoding="utf-8")
        except Exception as error:  # noqa: BLE001 - one failure must not stop the benchmark
            row["error"] = str(error)
            row.setdefault("metrics", {"crisp_score": None, "words": None, "longest_sentence": None,
                                       "sentences_over_limit": None})
        print(f"done {tag}" + (f" ERROR {row['error'][:80]}" if row.get("error") else ""), flush=True)
        return row

    with cf.ThreadPoolExecutor(args.jobs) as pool:
        rows = list(pool.map(one, jobs))

    meta = {"date": date, "runs": args.runs, "claude_version": version, "isolated": isolated,
            "conditions": [name for name, _ in conditions]}
    summary = write_report(out, conditions, scenarios, rows, meta)
    (out / "results.json").write_text(json.dumps({"meta": meta, "summary": summary, "rows": rows}, indent=1),
                                      encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    print((out / "RESULTS.md").read_text())


if __name__ == "__main__":
    main()
