Rotate AWS access keys by adding a second key, switching every user to it, and deleting the old key last.

- Create the second key first, because an IAM user can hold two active keys at once.
- Deactivate the old key, do not delete it, and watch CloudTrail and error logs for a few days for failed requests that still use it.
- Delete the old key only after nothing has used it for a while, because deletion is permanent and breaks any remaining user at once.
