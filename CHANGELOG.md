# Changelog

## 1.2.0 - 2026-10-12

### Fixed
- Crisp 1.1.0 cut useful content on technical questions. A blind pairwise judge preferred the answer with no plugin in 30 of 36 pairs, because 1.1.0 dropped alternatives, troubleshooting steps, examples, and some safety warnings. The 1.1.0 README claim "shorter did not mean missing" was wrong.
- With 1.2.0, the same judge prefers the Crisp answer in 18 of 36 pairs and the answer with no plugin in 8.

### Changed
- New core rule: Crisp changes how an answer is written, never what it contains. Crisp removes only filler, repetition, preambles, closers, and restatements.
- Removed the length limits ("a simple question gets one to three sentences", "maximum seven bullets"). A long list is split into labeled groups, not cut.
- New completeness rules E9 to E14: keep alternatives, troubleshooting, every safety note, and useful examples and code. If unsure, keep the fact. A request for depth wins.
- The self-check compares the answer with the answer that Claude would give without Crisp.
- Answers keep the same content as a normal answer, in fewer words, and add no new topics.
- Creative writing (poems, stories, jokes) is exempt from the rules.
- `/crisp:tldr` keeps the first sentence to the main point and puts the steps in the bullets.

### Added
- Evaluation suite (`evals/run_suite.py`) with 22 pass/fail gates (`evals/gates.json`) for every mode: answer content (blind pairwise audit in both orders, must-cover facts), readability, strict level, on-demand mode, TL;DR, clarify, check, and guardrails (requests for depth, code, creative writing, no mention of Crisp).
- The suite runs in isolated setups, retries failed calls, can resume, and marks a gate INCOMPLETE (a failure) when data is missing.
- New README with the benchmark results, a real before-and-after example, and diagrams.

## 1.1.0 - 2026-10-11

### Added
- Completeness rules (Part E, E1 to E8). Short does not mean missing. A conditional answer starts with "Yes, if X". Every caveat that changes the action stays. These rules win over every shortening rule.
- Docs mode (`references/docs.md`): rules F1 to F10 and patterns for READMEs, runbooks, error messages, release notes, incident reports, commit messages, PR descriptions, API references, and UI text.
- Mode option: `always` (Crisp applies to every answer) or `on-demand` (Crisp applies only when you ask). Claude Code shows a one-line notice in the first session after install, and after each mode change.
- Reply check (Stop hook): after each answer, the checker scores the reply. `notify` shows a one-line warning. `fix` asks Claude to rewrite the answer one time. `off` turns it off.
- `/crisp:level on` turns Crisp on for one session in on-demand mode.
- Checker: `--type doc` (20 words for steps, 25 for descriptive paragraphs), a check for a bare "Yes." or "No." opening, and `--version`.
- Test suite (`tests/`), benchmark with a blind judge and must-cover facts (`evals/`), and CI.
- Codex plugin (`.codex-plugin/`, `.agents/plugins/marketplace.json`).
- ChatGPT skill (`portable/chatgpt-skill/`).

### Changed
- The session rules now hold the key document rules, so Crisp does not depend on opening a file. Crisp never mentions its own rules or files in an answer.
- The main skill no longer says "use for any chat answer". Claude loads it on its own only when Crisp is on or the user asks.
- All portable prompts (ChatGPT, Gemini, AGENTS.md) include the completeness rules.

## 1.0.0 - 2026-10-11

- First version: the crisp skill (answer shape, sentence, and word rules), `/crisp:clarify`, `/crisp:tldr`, `/crisp:check`, `/crisp:level`, the SessionStart hook, the output style, the checker, and portable prompts.
