Yes, after a rebase you must force push, but use `--force-with-lease` instead of plain `--force`. A rebase rewrites your commits, so the remote branch and your local branch no longer share the same history, and Git rejects a normal push for that reason.

The command is:

```
git push --force-with-lease
```

This option works like `--force`, but it refuses to overwrite the remote branch if someone else pushed new commits that you have not fetched. Plain `--force` would delete their work without a warning.

Before you push, make sure that the branch is yours alone, or that your team agrees to rewrite its history. Never force push to a shared branch such as `main`. If other people work on your feature branch, tell them first, because they will need to reset their local copies after your push.
