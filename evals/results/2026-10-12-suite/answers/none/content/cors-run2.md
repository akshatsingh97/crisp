Fix it on the API server. The server must send CORS headers that allow your frontend's origin. Changing the frontend cannot fix it.

**Why it happens**

The browser blocks a response when the API's origin differs from the page's origin. Origin means scheme, host, and port. For example, `http://localhost:3000` calling `http://localhost:8000` is cross-origin. The API must reply with `Access-Control-Allow-Origin` to permit the call.

**Fix by framework**

Express:
```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000' }));
```

FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"])
```

Flask:
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

Other servers: add the header `Access-Control-Allow-Origin: <your frontend origin>` to responses.

**Check these common problems**

1. **Preflight requests.** The browser sends an `OPTIONS` request first if you use `PUT`, `DELETE`, JSON bodies, or an `Authorization` header. The server must answer it with status 2xx and also send `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`. Most CORS libraries do this for you.
2. **Cookies or credentials.** If you send `credentials: 'include'`, set `Access-Control-Allow-Credentials: true`. The allowed origin must then be exact. A `*` value does not work with credentials.
3. **Errors without headers.** A 500 error or a redirect can lack the CORS headers. The browser then shows the CORS message and hides the real error. Check the server logs.
4. **Proxy or gateway.** Nginx, API Gateway, or a CDN can strip or not add the headers. Set them there if the proxy answers the request.
5. **Wrong order.** Register the CORS middleware before your routes.

**Development shortcut**

Use your dev server's proxy, for example Vite's `server.proxy` or the `proxy` field in Create React App. The browser then sees the same origin, and you need no CORS setup in development.

Avoid `Access-Control-Allow-Origin: *` in production, unless the API is public and uses no cookies.

If it still fails, send me the request URL, your server framework, and the response headers from the browser's Network tab. I can then find the exact cause.
