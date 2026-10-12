Yes, if only you use the branch. Use `--force-with-lease` instead of `--force`.

A rebase rewrites your commits, so they no longer match the commits on the remote. Git rejects a normal push to protect the remote history.

`--force-with-lease` replaces the remote branch only if it still matches what you last fetched. If a teammate pushed new commits, the push fails. Plain `--force` overwrites their work without a warning.

1. Run `git fetch origin` to update your view of the remote.
2. Run `git log --oneline HEAD..origin/<branch>` to see remote commits you do not have. If it lists commits you do not recognize, stop and ask the author.
3. Run `git push --force-with-lease origin <branch>`.

Warnings:
- Never force push to a shared branch such as `main` or `develop`. Other people lose commits and must repair their clones.
- If a teammate has your branch checked out, they must run `git fetch` and then `git reset --hard origin/<branch>`. A normal `git pull` will create a messy merge. Warn them first.
- If the push fails with "stale info", the remote changed after your last fetch. Fetch again, review the new commits, and rebase onto them if needed.

If the branch has an open pull request, the request will update after the push. Old review comments can lose their position in the diff.
