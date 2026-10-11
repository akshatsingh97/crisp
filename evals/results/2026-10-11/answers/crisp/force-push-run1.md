Yes, but use `git push --force-with-lease`, and only if the branch is yours alone. A rebase rewrites commit history, so the remote branch no longer matches your local one. A normal push is rejected for that reason.

`--force-with-lease` is safer than `--force`. It refuses to push if someone else added commits to the remote branch since your last fetch.

1. Run `git fetch` to update your view of the remote.
2. Run `git log HEAD..origin/<branch>` to check for commits from other people.
3. If that list is empty, or you know those commits are in your rebase, run `git push --force-with-lease`.

Risks:
- If a teammate also works on this branch, a force push can erase their commits. Tell them first. They must then rebase or reset their copy.
- Never force push to a shared branch such as `main`.
- If the branch has an open pull request, the force push updates it. Existing review comments can lose their position in the diff.
