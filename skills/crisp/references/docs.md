# Crisp docs mode

Use these rules when you write or rewrite a document. Parts A to E of `SKILL.md` still apply. These rules add the structure that documents need.

## Rules F1 to F10

F1. **Classify each passage.** Procedural text tells the reader what to do. Descriptive text explains what a thing is or why it works. Do not mix the two in one paragraph.

F2. **Procedural text.**
- Use the imperative: "Install the CLI."
- Write one instruction per step, unless two actions happen at the same time.
- Use a maximum of 20 words per sentence.
- Put the condition first: "If the port is in use, stop the other process."
- After a step whose result is not obvious, give the expected result: "The terminal shows `Server ready on :3000`."

F3. **Descriptive text.**
- Use the simple present.
- Use a maximum of 25 words per sentence.
- Use one topic per paragraph, with a maximum of six sentences.
- Give one new fact per sentence.

F4. **Name the context of each step.** Say where to run a command (which host, directory, or shell), as which user, and what must already be done. "Run the migration" becomes "On the database host, run `npm run migrate` from the `api/` directory."

F5. **Warnings come before the step,** not after it. Start with the instruction or the condition, then give the risk.
- `Warning:` for data loss, security risk, or an action that cannot be undone.
- `Caution:` for downtime, cost, or damage that can be repaired.
- Example: "Warning: Do not run `db:reset` on production. The command deletes all rows."

F6. **One term, one meaning, in the whole document.** Pick one word for each concept before you write. If the document uses more than five special terms, add a short glossary.

F7. **Headings name the task or the topic.** Use "Install the CLI", not "Getting started with installation". A heading covers at least three sentences or one list.

F8. **Lists.** Use a numbered list for steps that must happen in order. Use bullets for three or more parallel items. End the lead-in sentence with a colon.

F9. **No marketing language in technical documents.** Delete "powerful", "seamless", "best-in-class", and "blazingly fast". Give the measured property instead: "Builds take 4 seconds on a 2024 laptop."

F10. **Put the most-used information first.** In a reference page, put the common case before the edge cases. In a troubleshooting page, put the most common cause first.

## Patterns by document type

### README

1. One sentence that says what the project does and for whom.
2. A short example of the result (output, screenshot, or code).
3. Requirements, with versions.
4. Install, as numbered steps.
5. Quick start: the shortest path to a working result.
6. Configuration: a table with name, default, and effect.
7. Troubleshooting: symptom, then cause, then fix.
8. License and contact.

### Runbook

1. **Trigger:** the alert or symptom that starts this runbook.
2. **Impact:** what users see, with numbers if known.
3. **Checks:** commands that confirm the cause, each with the expected output.
4. **Fix:** numbered steps. Put each warning before its step (F5).
5. **Verify:** how to know that the system is healthy again.
6. **Rollback:** how to undo the fix.
7. **Escalate:** who to call, and when.

Before:
> If the queue backs up you should probably restart the workers, but be careful since that can drop in-flight jobs if they haven't been acked yet.

After:
> If the queue has more than 10,000 messages, restart the workers.
>
> 1. Caution: A restart drops jobs that the workers did not acknowledge. Run `queue stats` and make sure that `unacked` is 0.
> 2. Run `systemctl restart worker@*` on each worker host.
> 3. Run `queue stats` again. The queue length decreases within 2 minutes.

### Error message

Give three parts, in this order:

1. What happened, in the simple past.
2. Why, if the code knows the cause.
3. What the user can do, as an imperative.

No blame, no "Oops", no apology filler. Keep the error code.

Before:
> Oops! Something went wrong while trying to save your changes. Please ensure you are connected and try again later.

After:
> Your changes were not saved. The connection to the server stopped. Check your network, then select Save again. (Error E1042)

### Release notes

1. Breaking changes first, with the warning pattern (F5). Each one says what the user must change.
2. New features: one sentence each. Say what the user can now do.
3. Fixes: say what was wrong, in the simple past.
4. Keep version numbers, flags, and configuration keys exact (E4).

Before:
> We've revamped the config loader to be more robust, so you may need to tweak a few settings.

After:
> Breaking: The configuration file is now `crisp.toml`, not `crisp.json`. Rename your file before you upgrade. Version 2.0 does not read the old file.

### Incident report

1. Summary: what failed, when (in UTC), for how long, and for how many users.
2. Timeline: one line per event, with the time in UTC.
3. Root cause: in the simple past, with active voice.
4. What went well, and what did not.
5. Actions: each with an owner and a date.

Before:
> We have identified an issue that may have impacted some users' ability to log in.

After:
> Between 14:02 and 14:31 UTC, 12% of login requests failed. A configuration change removed the certificate for `auth.example.com`.

### Commit message

- Subject: imperative, 50 characters or fewer, no period. "Fix timeout in the upload retry", not "Fixed timeouts".
- Body: what changed and why, not how. Wrap at 72 characters.
- Name the issue number if there is one.

### Pull request description

1. One sentence: what the PR changes.
2. Why the change is necessary.
3. How to test it, as numbered steps.
4. Risks and the rollback plan, if any.

### API reference

1. One sentence: what the endpoint or function does.
2. A table of parameters: name, type, required, default, description.
3. One example request and its response.
4. A table of errors: code, cause, fix.

### UI text

- Buttons: a verb that names the result ("Save draft", not "OK").
- Labels: nouns, two or three words.
- Empty states: what the area is for, then the action that fills it.
- Confirmation before a destructive action: name the object and the result. "Delete 3 files? You cannot undo this."
