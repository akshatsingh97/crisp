Rotate AWS keys by creating a second key, switching every user to it, then deleting the old key only after it goes unused.

- A user can hold two active keys, so you can add the new key before you touch the old one.
- Deactivate the old key first and watch CloudTrail and error logs for a few days for failed requests that still use it.
- Deleting a key is permanent and anything still using it breaks at once, so delete only after a quiet period.
