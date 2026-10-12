Use this message:

> **File is too large**
> The maximum file size is 25 MB. Your file is larger. Compress the file or split it into smaller parts, then upload again.

For a short version, such as a toast (small pop-up notice), use: "File is too large. The maximum size is 25 MB."

Two notes:
- Show `ERR_UPLOAD_413` only in small text or a "Details" link. Support staff need it, but end users do not.
- If the app can tell the user the file size, add it: "Your file is 31 MB." I assumed it cannot, so the message above leaves it out.
