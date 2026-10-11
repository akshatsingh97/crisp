You fix this error on the server, not in the frontend: your API must send an `Access-Control-Allow-Origin` header that names the origin of your frontend. An origin is the scheme, host, and port of a page, for example `http://localhost:3000`. The browser blocks the response because your API is on a different origin and does not say that the frontend may read it. This rule is called CORS (cross-origin resource sharing).

The exact change depends on your server. In Express, you install the `cors` package and allow your frontend origin:

```js
const cors = require("cors");

app.use(cors({ origin: "http://localhost:3000" }));
```

In Flask, you use the `flask-cors` package:

```python
from flask_cors import CORS

CORS(app, origins=["http://localhost:3000"])
```

If you cannot use a package, you set the header yourself on every response: `Access-Control-Allow-Origin: http://localhost:3000`. Replace the value with the real origin of your frontend. Use the production origin when you deploy.

If your request sends a custom header such as `Authorization`, uses a method other than GET or POST, or sends JSON with `Content-Type: application/json`, the browser first sends a preflight request (a check made with the OPTIONS method before the real request). Your server must answer that request with status 200 or 204 and with these headers: `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`, and `Access-Control-Allow-Origin`. The `cors` and `flask-cors` packages do this for you.

If your frontend sends cookies, set `credentials: "include"` in `fetch` and add `Access-Control-Allow-Credentials: true` on the server. In that case the allowed origin must be one exact origin. The value `*` does not work with credentials.

If the error remains after you make these changes, open the Network tab in your browser tools and look at the failed request. Make sure that the response contains the header. An error page from a proxy, a 500 response, or a wrong URL can also produce this message, because those responses do not carry the CORS headers.

Do not use a browser extension that turns off CORS, and do not use `origin: "*"` on an API that handles private data. Those options hide the problem on your machine and can cause a security problem in production.
