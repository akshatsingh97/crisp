---
name: level
description: Turn Crisp on, off, or strict for this session (on, lite, strict, off)
argument-hint: "on | lite | strict | off"
disable-model-invocation: true
---

Set the Crisp level for the rest of this session to: $ARGUMENTS

If the line above still shows a placeholder, use the word that the user wrote after the command.

- `on` or `lite`: apply Parts A to E of the crisp skill to every answer, until the user turns Crisp off. This works in both modes, `always` and `on-demand`.
- `strict`: apply lite, plus the strict word discipline in section 4 of the crisp skill's `references/vocabulary.md`.
- `off`: stop applying Crisp rules until the user turns them on again. Ignore the Crisp session rules from the start of the session.
- No value: tell the user the current level and mode in one sentence.

Reply with one sentence that confirms the new level. Write that sentence with the new level's rules.

To change the default for new sessions:
- Claude Code: open `/config` and change the plugin options "Crisp mode" (`always` or `on-demand`) and "Crisp level".
- Codex: set the environment variables `CRISP_MODE` and `CRISP_LEVEL` before you start Codex.
