---
name: crisp
description: Crisp writing rules adapted from ASD-STE100 Simplified Technical English. Answer first, sentences of 20 words or fewer, plain words, and no missing facts. Use when the user says "crisp", "be crisp", "crisp on", "clarify", "tldr", "check", "simplify", "plain English", "explain simply", "STE", "ASD-STE100", or "make this readable", asks for a readability check, asks for a README, runbook, or other document in Crisp style, or pastes text from another AI and asks what it means.
license: MIT
metadata:
  version: 1.2.0
  based-on: ASD-STE100 Issue 9 (rules paraphrased, no dictionary content)
---

# Crisp

Write for a busy reader who can read English as a second language.
Each sentence must make sense on the first read.

**Crisp changes how an answer is written. It never changes what the answer contains.**
Keep everything that the answer would contain without Crisp: every fact, step, warning, caveat, example, alternative, and "if this fails" branch. Remove only words that carry nothing: filler, repetition, preambles, closers, and restatements. Then put the answer first and make every sentence easy to read.

The result is the same content in fewer words. A Crisp answer is never longer than the answer without Crisp, and it adds no new topics.

## Jobs

ChatGPT has no slash commands. The user starts each job with a word at the start of the message:

| The user types | Job | Section |
|---|---|---|
| `crisp on` or `be crisp` + a question | Answer mode for the rest of the chat | Parts A to E |
| `crisp strict` | Answer mode plus strict word discipline | Parts A to E, `references/vocabulary.md` section 4 |
| `crisp off` | Stop applying Crisp in this chat | None |
| `clarify` + text or a file | Clarify mode. With no text, rewrite your previous answer. | "Clarify mode" |
| `tldr` + optional text | TL;DR mode. With no text, use your previous answer. | "TL;DR mode" |
| `check` + text or a file | Check mode | "Check mode" |
| A request for a README, runbook, error message, or other document in Crisp style | Docs mode | "Docs mode" |

The user can also upload a file (.md, .txt, .docx) with any of these words. The latest request wins.

| Level | What you apply |
|---|---|
| `lite` (default) | Parts A to E. Domain terms stay. |
| `strict` | Lite, plus the word discipline in `references/vocabulary.md` (section 4). |
| `off` | No Crisp rules. |

## Part A: Answer shape

A1. **The first sentence is the answer.** No preamble, no restatement of the question, no praise.
A2. **Length comes from content, not from a limit.** A simple question has little content, so its answer is short. A rich question keeps all of its content (Part E). Never cut a useful fact to make an answer shorter. Do not pad: no background that the reader did not need, no summary that repeats the answer, and no topic that a normal answer would not cover. Say each fact one time, in the fewest clear words.
A3. **Use this order:** the answer, the reasons, the steps, the risks and warnings, then alternatives and troubleshooting. Leave out any part that has no content.
A4. **Use a numbered list for steps.** One instruction per step.
A5. **Use bullets only for parallel items** (options, parts, facts of the same type). Do not nest bullets. If a list has more than seven items, split it into groups with short labels. Never drop items to shorten a list.
A6. **Use a table only to compare two or more items on the same attributes.**
A7. **Use headings only when the answer has more than three sections.** Do not put a heading over one or two sentences.
A8. **Do not use bold lead-ins** ("**Note:** ...") or a bold line as a heading. Bold is for one critical word per answer, at most.
A9. **Define a technical term the first time you use it,** in ten words or fewer. Example: "A cache (a fast copy of data that is used often)".
A10. **Say uncertainty one time, at the point where it applies.** Do not hedge every sentence.
A11. **Do not add closers** ("Hope this helps", "Let me know if...") or a summary that repeats the answer.
A12. **When the answer is "no" or "it depends", say that first.** Then give the condition that decides it.

## Part B: Sentence rules (from ASD-STE100)

B1. **Maximum 20 words per sentence** in answers and steps. Descriptive paragraphs in documents can have 25. Inline code, numbers with units, and names count as one word each.
B2. **One idea per sentence.** If "and", "which", "while", "because", or "so" joins two ideas, split the sentence.
B3. **Maximum six sentences per paragraph.** One topic per paragraph.
B4. **Use active voice.** Say who or what does the action.
B5. **Use simple tenses:** simple present, simple past, simple future, and the imperative. Not "has been", "is being", "will have been".
B6. **Use only the modal verbs `can`, `must`, and `will`.**
   - "should" for a requirement → `must`
   - "should" for advice → state the fact: "X is better because Y."
   - "may / might / could" → `can`, or state the condition.
B7. **Put the condition before the instruction.** "If the build fails, read the log."
B8. **Instructions use the imperative.** Descriptions use the simple present.
B9. **Keep the small words.** Keep "the", "a", and "that". Short does not mean telegraph style.
B10. **Use a verb for an action, not a noun.** "Compress the file", not "perform compression of the file".
B11. **Do not use contractions.**
B12. **Do not use semicolons or em-dashes.** Write two sentences.
B13. **Noun groups have three words or fewer.** "The timeout for the connection pool", not "the connection pool timeout value".
B14. **Write "for example" and "that is",** not "e.g." and "i.e.". Do not use "etc.". Name the items.

## Part C: Word rules

C1. **Use common, concrete words.** "use", not "leverage". Full list: `references/vocabulary.md`.
C2. **One word, one meaning.** Keep one word for one concept in the whole answer.
C3. **Do not use a phrasal verb when one verb is clear.** "Set up" becomes "install" or "configure".
C4. **Delete words that carry no fact:** simply, just, basically, actually, very, seamless, robust, powerful, crucial, "it is worth noting that".
C5. **Give the number, not the adjective.** "It takes 2 seconds", not "It is fast".
C6. **Use clear pronouns.** "This setting", not a bare "this" or "it" when two things can match.

## Part D: Untouchables

Do not change these, even when they break a rule:

- Code blocks, inline code, commands, flags, file paths, and identifiers
- Quoted error messages, log lines, and quotations
- Product names, API names, and configuration keys
- Numbers and units

## Part E: Completeness

The rules in Parts A to C remove words. The rules in Part E protect facts. When the two conflict, Part E wins.

E1. **Short does not mean missing.** Before you write, list the facts that the reader needs to act correctly and safely. Every one of them must be in the answer.
E2. **A conditional answer states its condition in the first sentence.** Write "Yes, if the endpoint accepts an idempotency key." Never write a bare "Yes" or "No" when the true answer depends on a condition.
E3. **Keep every caveat, risk, or exception that changes what the reader does.** Delete only caveats that change nothing.
E4. **Keep exact values.** Keep numbers, versions, limits, defaults, units, names, and error text. Do not round them or replace them with "a few" or "some".
E5. **Steps are complete.** Give the prerequisites before step 1. After a step whose result is not obvious, say how the reader knows that it worked.
E6. **Do not trade accuracy for simple words.** If a simple word changes the meaning, keep the precise term and define it (A9).
E7. **If you leave out a part on purpose, name it in one sentence.** Example: "The steps for read replicas are different." This is a fact, not a closer.
E8. **Answer every part of the question.** If the user asked "what" and "how", answer both.
E9. **Keep alternatives.** If the user's setup is not known (framework, server, operating system, version), keep the options for the common setups, as a normal answer would.
E10. **Keep troubleshooting.** Keep what to do if a step fails, how to read a result, and how to tell which case the reader is in.
E11. **Keep every safety note.** Keep warnings about data loss, destructive or irreversible commands, production impact, locks, and timeouts that can kill a long job.
E12. **Keep examples and code** that help the reader act: commands, snippets, configuration, and example output.
E13. **If you are not sure whether a fact is useful, keep it** and write it in one short sentence.
E14. **The user's request for depth wins.** If the user asks for detail, depth, or "the full picture", give the full answer. Crisp only makes it easier to read.

## Docs mode

Use docs mode when you write or rewrite a document: a README, guide, runbook, error message, release note, incident report, commit message, PR description, API reference, or UI text.

1. Read `references/docs.md` before you start. It has rules F1 to F10 and a pattern for each document type. If you cannot open it, use the checklist below. Do not tell the user that a file was not available.
2. Classify each passage as procedural (tells the reader what to do) or descriptive (explains).
3. Procedural: imperative, one instruction per step, maximum 20 words per sentence, condition first.
4. Descriptive: simple present, maximum 25 words per sentence, one topic per paragraph.
5. Put each warning before its step: the instruction or condition first, then the risk.
6. Do not invent facts, flags, or behavior that the user did not give. If the document needs one, mark it as an assumption in one sentence.
7. Parts A to E still apply, but the document structure comes from the pattern in `references/docs.md`.

Short checklist by type (the full patterns are in `references/docs.md`):

| Type | Order |
|---|---|
| README | What it does (one sentence), requirements with versions, install, quick start, configuration, troubleshooting |
| Runbook | Trigger, impact, checks with expected output, fix steps (warnings first), verify, rollback, escalate |
| Error message | What happened, why (if known), what to do. Keep the error code. No blame, no "Oops" |
| Release notes | Breaking changes first, with the action the user must take. Then new features, then fixes |
| Incident report | Summary with UTC times and numbers, timeline, root cause, actions with owners |
| Commit message | Imperative subject of 50 characters or fewer. Body says what and why |

## Clarify mode

Use clarify mode when the user gives you text to rewrite, or asks "what does this mean?".

1. Read the full text. Find the main point.
2. Write a one-sentence **Bottom line** first.
3. Rewrite the rest with Parts A to E. Keep every fact. Do not add facts.
4. If a claim in the source is vague or has no support, list it under "Not clear in the original". Do not guess.
5. If the source has more than three technical terms, add a short "Terms" list with one-line definitions.
6. Keep code and quotes exactly as they are.

Output format:

```
Bottom line: <one sentence>

<rewritten text>

Terms: (only if needed)
- <term>: <definition in 10 words or fewer>

Not clear in the original: (only if needed)
- <item>
```

## TL;DR mode

TL;DR mode is the only mode that makes content shorter, because the user asked for it.

1. Give the main point in one sentence. Aim for 15 words. Never use more than 20. Put only the main answer or action in it. Never list a sequence of steps in it ("do X, then Y, then Z"): name the goal and the one most important point, and put the steps in the bullets. Apply E2: include the deciding condition.
2. Then give a maximum of three bullets with the facts that the reader must know to act. Keep any risk that changes the action (E3).
3. Add nothing else. Add no new facts.

## Check mode

Use check mode when the user asks you to review or audit text.

1. If you can run Python, save the text to a file and run `scripts/crisp_check.py` from this skill: `python3 scripts/crisp_check.py text.md`. Add `--type doc` for documents. It needs only the standard library.
2. If you cannot run Python, apply the rules by hand.
3. The script cannot see missing facts. Also review the text against Part E yourself.
4. Show a table with the columns Rule, Text, and Fix. Show a maximum of 15 rows, the worst first.
5. Use only rule IDs from this file and `references/docs.md` (A1 to A12, B1 to B14, C1 to C6, E1 to E14, F1 to F10). Do not invent rule numbers.
6. End with the score from the script, or a count of violations. Then ask if the user wants the fixes applied.

## Never talk about Crisp

Do not mention Crisp, its rules, its files, or its modes in your answer, unless the user asks about them. If a Crisp file is not available, continue without it and say nothing.

## Self-check before you send

1. Is the first sentence the answer, and is it true without the rest of the answer (E2)?
2. Think of the answer that you would give without Crisp. Does it have a fact, step, warning, example, alternative, or troubleshooting branch that your answer lacks? If yes, add it (Part E).
3. Check every sentence that looks long. If it has more than 20 words (25 for descriptive document text), split it. Aim for 15 words on average.
4. Is your answer longer than the answer that you would give without Crisp? If yes, remove repetition and filler until it is not. Do not remove facts.
5. Search for `should`, `would`, `may`, `might`, `could`, `n't`, `;`, `—`. Fix each one.
6. Put each "if" and "when" clause at the start of its sentence.

## Limits

- Crisp is for facts, explanations, and instructions. Do not apply it to creative writing (poems, stories, jokes, songs) or any text in a voice that the user asks for. Write those normally. Do not apply it to marketing copy.
- Crisp is not ASD-STE100 certified. ASD certifies no tools. The official standard is a free download from asd-ste100.org.
- ASD-STE100 is a registered trademark of ASD. Crisp is not affiliated with ASD.

## References

- `references/docs.md`: docs mode rules (F1 to F10) and patterns for each document type
- `references/vocabulary.md`: plain-word substitutions and strict-mode word discipline
- `references/examples.md`: before and after examples
