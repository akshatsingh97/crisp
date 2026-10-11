---
name: clarify
description: Rewrite any text (for example, output from another LLM) into clear, simple English
argument-hint: "[text to rewrite, or a file path] (empty = your last answer)"
disable-model-invocation: true
---

Use the crisp skill in **clarify mode**.

Input: $ARGUMENTS

If the input line above still shows a placeholder, use the text that the user wrote after the command.

1. If the input is a file path that exists, read that file and rewrite its prose. Do not change code.
2. If the input is empty, rewrite your previous answer in this conversation.
3. Otherwise, rewrite the input text.

Follow the clarify-mode output format from the skill:

- `Bottom line:` one sentence with the main point.
- The rewritten text, with every fact, number, caveat, and step kept (Part E) and no new facts added.
- `Terms:` only if the text has more than three technical terms.
- `Not clear in the original:` only if the source has vague or unsupported claims.

Keep code blocks, commands, numbers, and quotes exactly as they are.
