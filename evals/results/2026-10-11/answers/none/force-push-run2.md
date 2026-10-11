Yes, after a rebase a force push is the normal way to update the remote branch. Use `--force-with-lease`, not plain `--force`.

```
git push --force-with-lease
```

**Why it's needed:** a rebase rewrites your commits, so your local history no longer extends the remote branch's history. Git rejects the push because it would discard the old commits on the remote.

**Why `--force-with-lease`:** it only overwrites the remote branch if it still points to the commit you last fetched. If a teammate pushed to the branch in the meantime, the push fails instead of silently deleting their work. Plain `--force` overwrites no matter what.

**Check these first:**
- **Branch ownership.** Force-pushing is fine on your own feature branch. Don't do it on `main`, `develop`, or any branch others build on.
- **Collaborators.** If someone else works on this branch, tell them. They'll need to rebase or reset their local copy after your push.
- **What you're pushing.** Run `git fetch` and then `git log origin/<branch>..HEAD` and `git log HEAD..origin/<branch>`. The second should show only the old, pre-rebase versions of your own commits, with nothing from someone else.

If the lease check fails, someone else pushed to the branch. Fetch, look at their commits, and rebase again before you retry.
