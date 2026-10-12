Yes, but use `--force-with-lease`, not plain `--force`, and only if the branch is yours alone. A rebase rewrites commit history, so the remote branch no longer matches yours. The rejection is expected.

Run this:

```
git push --force-with-lease origin <your-branch>
```

`--force-with-lease` refuses to push if the remote has commits you have not fetched. Plain `--force` would overwrite them without a warning.

Before you push:

1. Run `git fetch origin`. This updates your view of the remote so the lease check is accurate.
2. Run `git log HEAD..origin/<your-branch>`. If this shows commits, someone else pushed to the branch. Do not force push yet.
3. If you see their commits, ask them first. You can also rebase again on top of their work.

Warnings:

- A force push permanently replaces the remote history. Other people who based work on the old commits will have conflicts.
- Never force push to shared branches such as `main`. Many teams block it by branch protection.
- If the branch has an open pull request, a force push is normal and safe. Reviewers may need to re-pull, and some review comments can lose their line anchors.

If `--force-with-lease` is rejected with "stale info", run `git fetch` and check what changed on the remote. Then decide whether to rebase again or to overwrite.
