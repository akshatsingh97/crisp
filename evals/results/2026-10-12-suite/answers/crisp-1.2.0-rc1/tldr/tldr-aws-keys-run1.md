Rotate AWS keys by adding a second key, switching every user to it, then deactivating and later deleting the old one.

- Update every application, CI pipeline, and developer machine to the new key before you deactivate the old key.
- Deactivate the old key first, then wait a few days and watch CloudTrail and error logs for failed requests that still use it.
- Delete the old key only after nothing has used it for a while, because deletion is permanent and breaks anything still using it.
