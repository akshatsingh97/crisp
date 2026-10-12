Rotate AWS access keys by creating a second key, moving everything to it, and deleting the old key last.

- Update every application, CI pipeline, and developer machine to the new key, then deactivate the old key instead of deleting it.
- Wait a few days and watch CloudTrail and error logs for failed requests that still use the old key.
- Deleting a key is permanent and breaks anything still using it, so delete only after nothing has used it for a while.
