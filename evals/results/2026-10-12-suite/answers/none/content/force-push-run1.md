Yes, a rebase rewrites commits, so the remote branch and your local branch have diverged and a plain push is rejected. Force-pushing is the normal fix, but use the safer form:

```bash
git push --force-with-lease
```

`--force-with-lease` refuses to push if the remote branch has commits you haven't fetched. A plain `--force` would silently overwrite them.

Before you push:

- **Check the branch is yours alone.** If teammates also push to it, force-pushing will break their local copies. Tell them first, or don't rebase shared branches.
- **Run `git fetch` and `git log HEAD..origin/<branch>`.** If it shows commits you don't recognize, someone else pushed. Look at those before overwriting.
- **Never force-push `main` or `master`.** Protected branches will usually reject it anyway.

If a PR is open, it will update automatically. Reviewers may need to re-review, since line comments can lose their anchors after a rebase.
