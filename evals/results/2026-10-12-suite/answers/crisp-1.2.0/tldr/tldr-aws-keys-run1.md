Rotate AWS keys by creating a second key, switching every user to it, then deactivating and later deleting the old one.

- Update every application, CI pipeline, and developer machine to the new key, then deactivate the old key and watch CloudTrail and error logs for a few days.
- Delete the old key only after nothing has used it for a while, because deletion is permanent and anything still using it breaks immediately.
- Consider IAM roles or short-lived credentials so you do not need long-lived keys at all.
