---
name: tldr
description: Give the shortest useful version of your last answer (or of given text)
argument-hint: "[optional text]"
disable-model-invocation: true
---

Use the crisp skill.

Input: $ARGUMENTS

If the input line above still shows a placeholder, use the text that the user wrote after the command.

If the input is empty, use your previous answer. Otherwise, use the input text.

Write:

1. One sentence with the answer or the main point. Aim for 15 words. Never use more than 20. Put only the main answer or action in this sentence. Never list a sequence of steps in it ("do X, then Y, then Z"): name the goal and the one most important point, and put the steps in the bullets. If the answer depends on a condition, include the condition (rule E2).
2. Then a maximum of three bullets with the facts that the reader must know to act. Each bullet is one sentence. Keep any risk or caveat that changes what the reader does (rule E3).

Do not add anything else. Do not add new facts.
