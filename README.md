# Crisp

Crisp makes LLM answers clear, short, and complete. It gives the answer first, uses sentences of 20 words or fewer, uses plain words, and keeps every fact that the reader needs.

It works in Claude Code, Codex, Cowork, the Claude app, ChatGPT, Gemini, Cursor, Copilot, and any other LLM.

The rules come from **ASD-STE100 Simplified Technical English**, the controlled language that aerospace manuals use so that readers cannot misread an instruction:

- A restricted vocabulary (about 900 approved words in the official dictionary).
- A maximum of 20 words in each sentence.
- One idea in each sentence.

Crisp adds two rule groups that STE does not have:

- Answer shape: the answer comes first, the length matches the question, and there is no filler.
- Completeness: short does not mean missing. A conditional answer starts with "Yes, if X". Every caveat that changes what the reader does stays in. When a shortening rule and a completeness rule conflict, completeness wins.

## Before and after

Before (typical LLM output, answer in sentence 3):

> Great question! This is a common source of confusion for developers who are transitioning to server-side rendering. In short, no — `useEffect` doesn't run on the server. This is because effects are designed to run after the component has been mounted to the DOM, which only happens in the browser. Hope this helps!

After:

> No. `useEffect` runs only in the browser, after React adds the component to the page. On the server, React renders HTML and does not run effects. If you need data on the server, fetch it in a Server Component.

Too short (Crisp prevents this):

> Yes, the retry is safe because the endpoint is idempotent.

With Crisp:

> Yes, if each retry sends the same idempotency key as the first request. A timeout does not tell you if the first request arrived. Without a key, the retry can create a second order.

## Benchmark

12 tasks (8 developer questions and 4 document tasks), 2 runs each, Claude Code 2.1.296. Each setup ran in an empty HOME. A blind judge (a separate Claude session with no plugins) checked each answer against a list of facts that it must cover. The judge did not see which setup wrote the answer.

| Measure | No plugin | SimpleEnglish 2.1.1 | Crisp 1.1.0 |
|---|---|---|---|
| Fact coverage (judge) | 93% | 96% | **97%** |
| Accuracy (judge, 1 to 10) | 8.5 | 8.5 | 8.4 |
| Clarity (judge, 1 to 10) | 9.0 | 8.6 | 8.8 |
| Scan speed (judge, 1 to 10) | 8.9 | 7.3 | 8.5 |
| Words per answer | 224 | 213 | **192** |
| Sentences over 20 words, per answer | 1.0 | 2.2 | **0.2** |

What this shows:

- Crisp answers are 14% shorter than the answers with no plugin and have the highest fact coverage. Shorter did not mean missing.
- Accuracy and clarity stay at the level of the answers with no plugin. Differences of 0.1 to 0.4 points are within the noise for 24 answers.
- Claude Code's own style already scans well, so the gain there is in length and sentence discipline. The gain is larger in chat apps with longer default answers.
- The judge is a Claude model that judges Claude text, so family bias is possible.

Full results, every answer, and every judge note: `evals/results/`. Method and limits: `evals/README.md`.

## Is Crisp forced on you?

No. You choose when you install it, and you can change your mind at any time.

| Setting | Options | Default |
|---|---|---|
| Crisp mode | `always`: every answer uses Crisp. `on-demand`: Crisp works only when you ask. | `always` |
| Crisp level | `lite`, `strict`, or `off` | `lite` |
| Reply check | `notify`: a one-line warning when an answer breaks the rules. `fix`: Claude rewrites the answer one time. `off`. | `notify` |

- In Claude Code, change these settings in `/config`. The first session after install shows one line that says which mode is on and how to change it.
- In one session, run `/crisp:level off` or `/crisp:level on`, or just say "crisp off" or "crisp on". The latest request wins.
- In on-demand mode, the session rules tell Claude not to use Crisp until you ask. The main skill also does not load on its own for ordinary answers.
- In Codex, set `CRISP_MODE`, `CRISP_LEVEL`, and `CRISP_REPLY_CHECK` before you start Codex.
- In Cowork, ChatGPT, and the other tools, Crisp is always on-demand, because those tools have no session hook.
- To remove Crisp completely, disable or uninstall the plugin.

## What is in the package

| Part | What it does | Works in |
|---|---|---|
| `skills/crisp` | The rules: answer shape (A), sentences (B), words (C), untouchables (D), completeness (E), and docs mode (F, in `references/docs.md`) | Claude Code, Codex, Cowork, Claude app, Agent Skills tools |
| `skills/clarify` | `/crisp:clarify` rewrites any text, for example a ChatGPT answer | Claude Code, Codex, Cowork |
| `skills/tldr` | `/crisp:tldr` gives the shortest version that is still complete | Claude Code, Codex, Cowork |
| `skills/check` | `/crisp:check` audits text and shows fixes | Claude Code, Codex, Cowork |
| `skills/level` | `/crisp:level on\|lite\|strict\|off` changes the level for the session | Claude Code, Codex, Cowork |
| `hooks/session-start.sh` | Loads the rules at session start, by mode and level | Claude Code, Codex |
| `hooks/reply_check.py` | Checks each answer after Claude writes it | Claude Code |
| `output-styles/` | An output style named `crisp:crisp` | Claude Code |
| `skills/crisp/scripts/crisp_check.py` | A checker with no dependencies. It scores text from 0 to 100. | Python 3.8+ |
| `portable/` | ChatGPT skill, ChatGPT custom instructions, a system prompt for any LLM, and `AGENTS.md` | Any LLM |
| `tests/`, `evals/` | Unit tests and the benchmark | Development |

## Install

### Claude Code

```
claude plugin marketplace add akshatsingh97/crisp
claude plugin install crisp@crisp
```

To try it without an install, run `claude --plugin-dir ./crisp`.

Optional: to use the output style, run `/config` and select `crisp:crisp`.

### Codex

```
codex plugin marketplace add akshatsingh97/crisp
codex plugin add crisp@crisp
```

Codex asks you to trust the session hook before its first run. Open `/hooks` to approve it. The hook needs `sh` (macOS and Linux). Use the skills with `$`: `$clarify`, `$tldr`, `$check`, `$level`.

### Cowork and the Claude app

Download `crisp.plugin` from the [Releases page](https://github.com/akshatsingh97/crisp/releases) and install it. In Cowork, use `/crisp:clarify`, `/crisp:tldr`, and `/crisp:check`, or say "be crisp". To use only the main skill in the Claude app, upload `crisp-skill.zip` as a custom skill.

### ChatGPT

- If your plan has Skills, download `crisp-chatgpt.zip` from the [Releases page](https://github.com/akshatsingh97/crisp/releases) and upload it. Then type `crisp on`, `clarify`, `tldr`, or `check` at the start of a message.
- To apply Crisp to every chat, paste the block from `portable/chatgpt-custom-instructions.md` (1,428 characters) into custom instructions. On paid plans (5,000 characters), paste the full prompt from `portable/system-prompt.md`.

### Gemini, Perplexity, local models, and APIs

Paste the full prompt from `portable/system-prompt.md` into the Gem instructions, the Space instructions, or the system message.

### Cursor, Copilot, Gemini CLI, and other skills tools

Run `npx skills add akshatsingh97/crisp`, or copy `portable/AGENTS.md` to the root of your repository.

## Use

| You type | Result |
|---|---|
| Any question (mode `always`, or after "crisp on") | The answer follows the Crisp rules |
| `/crisp:clarify <text>` | A rewrite with a bottom line first, every fact kept, and a list of claims that are not clear |
| `/crisp:clarify` | A rewrite of the last answer |
| `/crisp:tldr` | The last answer in one sentence plus up to three bullets, with the deciding condition kept |
| `/crisp:check <file>` | A table of problems with fixes, and a score |
| `/crisp:level strict` | Full STE word discipline |
| "Write a runbook for ..." | Docs mode: steps separate from explanations, warnings before steps, a pattern for each document type |

## The checker

```
python3 skills/crisp/scripts/crisp_check.py answer.md
python3 skills/crisp/scripts/crisp_check.py README.md --type doc --fail-under 80
cat answer.md | python3 skills/crisp/scripts/crisp_check.py - --json
```

The checker finds:

- Sentences over the limit (20 words, or 25 for descriptive text with `--type doc`) and paragraphs with more than six sentences
- Banned modal verbs, contractions, semicolons, and dashes
- Perfect tenses, passive voice, and conditions after the main clause
- Filler words, inflated words, preambles, closers, and a bare "Yes." or "No." opening
- Bold lead-ins, bold lines used as headings, nested bullets, long lists, and word rotation

It ignores code blocks and inline code. It cannot see missing facts, so check mode also reviews the text against the completeness rules.

## Development

```
python3 -m unittest discover tests        # checker, hooks, and package tests
python3 tools/build_chatgpt_skill.py      # rebuild the ChatGPT copy after a skill change
python3 evals/run_bench.py --runs 2       # benchmark: none vs crisp
claude plugin validate .                  # Claude Code manifest
```

CI runs the unit tests on Python 3.8 and 3.12 and validates the plugin. When you change a rule, run the benchmark before and after, and commit the new results folder with the change.

## Compared with SimpleEnglish

[AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) gave Crisp the idea to apply STE to LLM output. The two projects make different choices:

- SimpleEnglish writes chat replies as prose only, with no lists. Crisp allows numbered steps and short lists, because readers find the action faster.
- Crisp adds completeness rules, an on-demand mode, and the clarify and TL;DR commands. It also adds the reply check and ChatGPT support.
- SimpleEnglish has a longer history, a 53-rule catalog for STE audits, and a dictionary extraction tool for strict compliance.

## Limits

- Crisp is for facts, explanations, and instructions. Do not use it for fiction or marketing copy.
- Crisp does not include the ASD-STE100 dictionary, because ASD owns the copyright. The official standard is a free download from asd-ste100.org.
- No tool makes text STE-certified. ASD certifies no tools.
- ASD-STE100 is a registered trademark of ASD. Crisp is not affiliated with ASD.

## License

MIT. See `CHANGELOG.md` for the version history.
