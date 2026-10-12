Rotate AWS access keys by adding a second key, switching every user of the old key, and deleting the old key only after it goes unused.

- Create a second access key for the IAM user (a user can hold two active keys), then update every application, CI pipeline, and developer machine to use it.
- Deactivate the old key first, not delete it, and watch CloudTrail and error logs for several days for failed requests that still use it.
- Delete the old key only when nothing has used it for a while, because deletion is permanent and anything still using it breaks immediately.
