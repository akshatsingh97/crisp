# Crisp evaluations

Crisp makes answers easier to read. The risk is that it also makes them less useful. The evaluations here measure both, and the gates in `gates.json` decide pass or fail.

There are three layers:

| Layer | What it checks | Needs a model | Command |
|---|---|---|---|
| Unit tests | The checker, both hooks, package consistency, the suite logic, and that no length limit returns to the rules | No | `python3 -m unittest discover tests` |
| Evaluation suite | Every Crisp mode against Claude with no plugin, with 22 pass/fail gates | Yes | `python3 evals/run_suite.py` |
| Benchmark | Must-cover facts and readability for any set of plugins, for example Crisp against SimpleEnglish | Yes | `python3 evals/run_bench.py` |

## The evaluation suite

`run_suite.py` runs Claude Code with no plugin (the baseline) and with each Crisp version that you name (the candidates). Every run uses an empty HOME, so your own plugins and settings cannot change the result. If isolation is not possible, the suite stops instead of running with your settings.

### Suites

| Suite | What runs | What is measured |
|---|---|---|
| content | 18 scenarios in 7 categories (safety, debugging, decisions, alternatives, depth, code, documents), 2 runs each | Information cut and added, preference, must-cover facts, accuracy, readability, length |
| strict | 6 scenarios at the strict level | Content kept, readability compared with lite |
| on_demand | 3 ordinary questions in on-demand mode | Crisp must not load |
| tldr | `/crisp:tldr` on 2 long texts, each with one critical caveat | Format, and the caveat kept |
| clarify | `/crisp:clarify` on 2 texts with known facts | Every fact kept, no fact added, bottom line first |
| check | `/crisp:check` on a text with known problems | Only real rule IDs |
| creative | A request for a poem | Crisp does not make it worse |

Every candidate output is also scanned for mentions of Crisp or its rules.

### How the content judge works

The content suite asks the main question: does Crisp remove useful information?

1. A judge (a separate `claude -p` run with no plugins) sees the baseline answer and the Crisp answer as X and Y. It does not know which tool wrote which answer.
2. It lists every piece of useful information that only one answer has: facts, steps, warnings, caveats, commands, examples, and alternatives. Wording and formatting do not count.
3. It rates each item: critical (without it, the reader can make a mistake or lose data), useful, or minor.
4. It picks the more useful answer.
5. The suite runs the judge a second time with X and Y swapped. Judges tend to favor one position, and two orders cancel that. A pair is a win or a loss only if both orders agree. The item counts are averaged.

A second judge checks each answer against 4 or 5 must-cover facts and scores accuracy.

### The gates

| Gate | Rule |
|---|---|
| G1, G2 | Crisp cuts no more critical items than it adds, and at most 0.1 per answer |
| G3 | Useful items cut divided by useful items added is 1.25 or less |
| G4 | The judge does not prefer the answer with no plugin more often |
| G5, G6 | Must-cover coverage and accuracy do not drop |
| G7, G8 | Readability score of 85 or more, and few sentences over the limit |
| G9 | Answers are not more than 10% longer than with no plugin |
| G10 | A request for depth gets at least 85% of the full length |
| G11 | Code in answers compiles |
| G12 | No answer mentions Crisp or its rules |
| G13, G14 | Strict level keeps content and readability |
| G15 | On-demand mode does not load Crisp |
| G16, G17 | TL;DR format, and the critical caveat kept |
| G18 to G20 | Clarify keeps every fact, adds none, and starts with a bottom line |
| G21 | Check cites only real rule IDs |
| G22 | Creative writing is not made worse |

`gates.json` has the exact thresholds and the reason for each one.

### Run it

```
python3 evals/run_suite.py
python3 evals/run_suite.py --candidate old=../crisp-1.1.0 --candidate new=.
python3 evals/run_suite.py --suites tldr,clarify,check --runs 1
python3 evals/run_suite.py --only pg-index,retry-code --suites content --runs 1
```

The results go to `evals/results/<date>-suite/`. `SUITE.md` is the scorecard. `metrics.json` has every number, and the `answers/` and `judge/` folders have every output and verdict. The exit code is 1 if a gate fails.

A full run makes about 400 model calls and takes 20 to 30 minutes with `--jobs 14`.

## Rules for changes

1. Run the unit tests for every change.
2. Run the full suite before and after any change to the rules in `skills/crisp/SKILL.md`, `hooks/context/`, or `portable/`.
3. Commit the new results folder with the change.
4. A change that fails a gate does not ship. To change a gate, explain why in the pull request.

## Limits

- The judge is a Claude model that judges Claude text. Family bias is possible.
- Each run samples the model, so the numbers move between runs. Treat small differences as noise, and use more runs (`--runs 3`) to confirm a close result.
- The readability gates use Crisp's own checker, which favors Crisp. The content gates do not use the checker.
- The scenarios are developer questions and documents. Results for other topics can differ.
