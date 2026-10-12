Yes, but use `--force-with-lease`, not plain `--force`, and only if you are the sole person who pushes to that branch.

A rebase rewrites commit history. Your local commits now have new hashes, so the remote branch no longer matches. Git rejects the push because it cannot fast-forward. This is expected after a rebase.

1. Check what you are about to overwrite:
   ```
   git fetch origin
   git log --oneline origin/<branch> ^<branch>
   ```
   If this lists commits you do not recognize, stop. A teammate pushed work that your rebase does not include.

2. Push with the safety check:
   ```
   git push --force-with-lease origin <branch>
   ```
   This fails if the remote has commits you have not fetched. Plain `--force` overwrites them without warning.

Warnings:
- A force push permanently replaces the remote history. Any commits only on the remote are lost, unless someone has a local copy.
- Never force push to a shared branch such as `main` or `develop`.
- If others work on your feature branch, tell them first. They must run `git fetch` and `git rebase origin/<branch>` or reset to the new history.

If `--force-with-lease` is rejected with "stale info", run `git fetch origin`, inspect the new remote commits, rebase onto them, and try again.
