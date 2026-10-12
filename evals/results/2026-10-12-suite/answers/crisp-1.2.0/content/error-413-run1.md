**File too large**

This file is too large to upload. The maximum size is 25 MB. Choose a smaller file, or compress this one, then try again.

Short version for a small alert or toast:

> This file is over the 25 MB limit. Choose a smaller file and try again.

I removed the error code and the technical terms ("request entity", "payload"), because end users cannot act on them. Keep `ERR_UPLOAD_413` in your logs for support. If you want users to report it, you can add a small "Error code: UPLOAD_413" line under the message.
