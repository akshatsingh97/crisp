# Changelog

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
