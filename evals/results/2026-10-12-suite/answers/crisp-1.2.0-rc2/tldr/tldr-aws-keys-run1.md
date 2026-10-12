Rotate AWS keys by adding a second key, switching every user to it, then deactivating and finally deleting the old one.

- Create the second key first, because an IAM user can hold two active keys, then update every application, CI pipeline, and developer machine.
- Deactivate the old key and wait a few days while you watch CloudTrail and error logs for failed requests that still use it.
- Delete the old key only after nothing has used it for a while, because deletion is permanent and anything still using it breaks at once.
