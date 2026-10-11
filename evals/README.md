# Crisp benchmark

The benchmark measures two things that pull against each other: readability and completeness. A writing plugin that only shortens answers can win on readability and still lose facts. This benchmark catches that.

## What it does

1. It asks Claude Code each prompt in `scenarios.json`, once per condition (for example, no plugin and Crisp).
2. It scores each answer with the Crisp checker: score, words, and longest sentence.
3. A blind judge scores each answer. The judge is a separate `claude -p` run with no plugins. It sees the request, the answer, and the facts that a good answer must cover. It does not see the condition name. It marks each fact as covered or not, and scores accuracy, clarity, and scan speed from 1 to 10.

## Run it

```
python3 evals/run_bench.py
python3 evals/run_bench.py --conditions none,crisp,simple-english=../SimpleEnglish --runs 3
python3 evals/run_bench.py --only charge-retry,pg-index --no-judge
```

The results go to `evals/results/<date>/`. `RESULTS.md` has the summary table.

If `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` is set, each run uses an empty HOME, so your own plugins do not change the result. Without one of them, disable your installed copy of Crisp before you run the benchmark.

## Add a scenario

Add an object to `scenarios.json`:

- `id`: a short name
- `type`: `reply` (a chat question) or `doc` (a document task)
- `prompt`: the request
- `must_cover`: three to five facts that a correct, complete answer must state

Write each fact so that a reviewer can mark it true or false. "Use CREATE INDEX CONCURRENTLY" is good. "Explains indexes well" is not.

## Rule for changes

When you change a rule in `skills/crisp/SKILL.md` or `hooks/context/`, run the benchmark before and after. Commit the new `evals/results/<date>/` folder with the change. A change that lowers fact coverage or accuracy needs a reason in the pull request.
