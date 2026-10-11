Here is a version for end users that keeps the 25 MB limit and the error code, so support can still trace the problem:

```
This file is too large to upload. The limit is 25 MB.
If your file is larger than 25 MB, compress it or split it into smaller files. Then upload it again.
Error code: ERR_UPLOAD_413
```

The message says what went wrong, states the limit, and gives the next step. It drops the technical terms "request entity" and "payload". The code stays at the end because users can quote it if they contact support.
