Yes, a push after a rebase needs a force, but use `--force-with-lease` instead of `--force`, and only if you are the sole user of the branch.

A rebase rewrites commit history. Your local commits have new hashes, so the remote branch no longer matches your history. Git rejects a normal push for that reason.

`--force-with-lease` refuses to overwrite the remote branch if someone else pushed commits you have not fetched. Plain `--force` overwrites them without any check.

1. Run `git fetch origin`.
2. Run `git log --oneline HEAD..origin/<branch>` to see remote commits you do not have. If the output is empty, nobody else pushed.
3. Run `git push --force-with-lease origin <branch>`.

If other people also work on this branch, tell them before you push. Their local copies will diverge from the rewritten history. They must rebase or reset their copies after your push.

If step 2 lists commits you do not recognize, do not force push. Those commits will be lost. Rebase your branch onto `origin/<branch>` again, or ask the author first.

If the push fails with "stale info", the remote changed after your last fetch. Fetch again and repeat from step 2.

Never force push to a shared branch such as `main`. If you overwrite something by mistake, you can often recover the old commits from `git reflog` locally, or from the remote host's branch history.
