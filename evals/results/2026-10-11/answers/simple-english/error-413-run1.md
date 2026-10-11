Here is a rewrite that tells the user what happened and what to do next:

```
This file is too large to upload. The limit is 25 MB.
If you can, compress the file or choose a smaller one, then try again.
```

I removed "Request entity too large" and "Payload" because most users do not know those terms. I kept the 25 MB limit because users need that number to fix the problem. You can keep `ERR_UPLOAD_413` in your logs, or show it in small text for support staff to use.
