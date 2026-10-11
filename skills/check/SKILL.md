---
name: check
description: Audit text for Crisp / STE rule violations and show fixes
argument-hint: "[file path or text] (empty = your last answer)"
disable-model-invocation: true
---

Use the crisp skill in **check mode**.

Input: $ARGUMENTS

If the input line above still shows a placeholder, use the text that the user wrote after the command.

1. Get the text. If the input is a file path, use that file. If the input is empty, use your previous answer. Otherwise, save the input text to a temporary file.
2. Run the checker. It is `skills/crisp/scripts/crisp_check.py` in this plugin:
   - Claude Code: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/crisp/scripts/crisp_check.py" <file>`
   - Codex and other tools: find the file `../crisp/scripts/crisp_check.py` next to the folder of this skill, then run `python3 <that path> <file>`.
3. If Python is not available, apply the rules by hand.
4. Show a table with these columns: Rule, Text, Fix. Show a maximum of 15 rows, the worst first.
5. Give the score from the checker in one sentence.
6. Ask one question: "Do you want me to apply the fixes?" Do not change files before the user says yes.

The checker cannot see missing facts. Also review the text against Part E (completeness) of the crisp skill, and add any E-rule problems to the table.

If the text is a document (README, runbook, guide), add `--type doc` to the checker command.

Use only the rule IDs from the crisp skill and its `references/docs.md` (A1 to A12, B1 to B14, C1 to C6, E1 to E8, F1 to F10).
