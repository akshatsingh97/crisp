Use this message:

> **File too large**
> This file is larger than 25 MB, so we cannot upload it. Compress the file or split it into smaller parts. Then try again.

Short version for a small toast or banner:

> This file is over the 25 MB limit. Choose a smaller file and try again.

- The code `ERR_UPLOAD_413` and the words "Request entity too large" mean nothing to end users. Show them only in logs or a "Details" link for support.
- The message states the limit (25 MB), so users know the target size.
- The message gives a next step. I assumed that compressing or splitting the file is possible for your users.
