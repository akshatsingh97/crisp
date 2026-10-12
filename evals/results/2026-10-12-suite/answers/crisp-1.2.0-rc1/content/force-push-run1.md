Yes, but use `--force-with-lease`, not plain `--force`, and only if nobody else has pushed to this branch.

A rebase rewrites your commits, so your local history no longer matches the remote branch. Git rejects the push for that reason. A force push is the normal fix for a rebased branch.

**Steps**

1. Check what the remote has that you do not: `git fetch` then `git log HEAD..origin/<branch>`. If the output is empty, nobody added commits you would lose.
2. Push with `git push --force-with-lease`.

`--force-with-lease` fails if the remote branch changed since your last fetch. Plain `--force` overwrites those changes without warning, and the lost commits are hard to recover.

**Risks**

- Never force push to a shared branch such as `main` or `develop`.
- If a teammate also works on your feature branch, tell them first. They must run `git fetch` and `git rebase origin/<branch>` or reset to the new history. Otherwise their next push can bring the old commits back.
- If `--force-with-lease` is rejected, someone pushed new commits. Fetch, review them, and rebase onto them again before you retry.

**Alternative**

If the branch is shared and you cannot force push, merge the target branch into your branch instead of rebasing. A normal push then works.
