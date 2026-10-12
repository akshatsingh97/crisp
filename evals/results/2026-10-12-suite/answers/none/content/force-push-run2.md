Yes, if the branch is yours alone. After a rebase, the rejection is expected. Rebase rewrites your commits, so your local history no longer extends the remote history.

Use `--force-with-lease` instead of plain `--force`:

```
git push --force-with-lease origin your-branch
```

It refuses to push if someone added commits to the remote branch that you have not fetched. Plain `--force` would delete those commits without a warning.

Check these first:

1. Run `git fetch` and `git log HEAD..origin/your-branch`. If this shows commits that you do not know, someone else pushed to the branch. Talk to them before you overwrite their work.
2. Do not force-push `main`, `master`, or any shared branch.
3. If a teammate has the branch checked out, they must run `git fetch` and `git reset --hard origin/your-branch` after your push. A normal `git pull` would merge the old and new history together.
4. If the branch has an open pull request, the push updates it. Review comments on old commits can become outdated.

If you do not want to rewrite history, you can instead merge the target branch into your feature branch. That push works without force, but it adds a merge commit.
