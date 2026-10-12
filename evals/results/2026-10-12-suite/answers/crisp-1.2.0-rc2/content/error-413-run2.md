Here is a rewrite for end users:

> **This file is too large to upload**
>
> The maximum file size is 25 MB. Your file is bigger than that. Compress the file or split it into smaller parts, then try again.
>
> Error code: ERR_UPLOAD_413

Notes:
- The error code stays at the bottom so support can still find it.
- "Request entity too large" and "payload" are removed because they mean nothing to most users.
- The 25 MB limit stays so users know the target size.

If you know the actual file size, you can add it: "Your file is 31 MB. The maximum is 25 MB."
