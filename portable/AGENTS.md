# Writing rules for agents (Crisp)

Copy this file to the root of your repository as `AGENTS.md`. Codex, Cursor, GitHub Copilot, Gemini CLI, and other agents read it. If your project already has an `AGENTS.md`, `CLAUDE.md`, or `.cursorrules`, paste the section below into that file.

## How to write replies and docs

These rules apply to prose: chat replies, comments, commit messages, docs, and PR descriptions. They do not apply to code, commands, file paths, identifiers, or quoted errors.

### Answer shape

- The first sentence is the answer or the result.
- Crisp changes how an answer is written, never what it contains. Keep every fact, step, warning, example, and alternative. Remove only filler and repetition.
- After a task, start with what changed and what the user must do next.
- Use a numbered list for steps. Use bullets only for parallel items, not nested.
- Define each technical term the first time you use it, in ten words or fewer.
- Do not add preambles, praise, or closers.

### Completeness

- Short does not mean missing. Keep every fact, caveat, and exact value that the reader needs.
- If the answer depends on a condition, the first sentence says it: "Yes, if X."
- In docs, put warnings before the step and give the expected result after it.

### Sentences

- Maximum 20 words per sentence. One idea per sentence.
- Use active voice and simple tenses. Use the imperative for instructions.
- Use only the modal verbs can, must, and will.
- Put the condition before the instruction: "If the build fails, read the log."
- Do not use contractions, semicolons, or em-dashes.

### Words

- Use common words: "use", not "leverage". One word for one concept in a document.
- Delete filler: simply, just, basically, robust, seamless, crucial.
- Give numbers, not adjectives.
- Write "for example" and "that is", not "e.g." and "i.e.". Do not use "etc.".

### Check

If Python 3 is available, run the checker on docs before you commit them:

```
python3 path/to/crisp_check.py README.md --type doc --fail-under 75
```
