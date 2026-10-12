Yes, but use `--force-with-lease`, not plain `--force`. After a rebase your local history differs from the remote, so a normal push is rejected. A force push is the expected fix.

```
git push --force-with-lease
```

Why `--force-with-lease`: it refuses to push if the remote branch has commits you have not fetched. Plain `--force` would overwrite them silently.

Risks:
- A force push rewrites the remote branch. Commits that exist only there are lost.
- If others work on this branch, tell them first. They must rebase or reset their copies.
- Never force push to a shared branch such as `main`.

If `--force-with-lease` is rejected, run `git fetch`, then check `git log origin/<branch>` for commits you do not have. Rebase onto them, or confirm they are safe to drop, then try again.
