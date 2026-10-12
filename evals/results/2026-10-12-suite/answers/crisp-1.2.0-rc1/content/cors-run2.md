Fix this on the API server. The server must send CORS (Cross-Origin Resource Sharing) headers that allow your frontend origin. You cannot fix it in the frontend code.

## Why it happens

The browser blocks a response when the frontend origin differs from the API origin. An origin is scheme, host, and port. For example, `http://localhost:3000` and `http://localhost:8080` are different origins. The browser allows the response only if the API sends `Access-Control-Allow-Origin` with a matching value.

## Steps

1. Find the exact origin of your frontend, such as `https://app.example.com`. Do not add a trailing slash.
2. Add CORS handling to the API. Pick your framework below.
3. Handle the preflight request. This is an automatic `OPTIONS` request that the browser sends before some calls. It happens for JSON bodies, `Authorization` headers, and methods like PUT or DELETE. The API must answer it with status 200 or 204 and the CORS headers.
4. Restart the API and reload the frontend. Open the browser DevTools Network tab and check the response headers.

## Examples

Express (Node.js):

```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000' }));
```

FastAPI (Python):

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Flask (Python):

```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

Spring Boot (Java), on a controller or method:

```java
@CrossOrigin(origins = "http://localhost:3000")
```

Any other server must send these headers:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Warnings

- If your requests send cookies or use `credentials: 'include'`, you cannot use `*` as the allowed origin. Name the exact origin and also send `Access-Control-Allow-Credentials: true`.
- Do not use `*` in production for an API with private data. Allow only the origins you trust.
- Do not copy the `Origin` request header into the response without checking it against an allow list. That lets any site call your API.

## If it still fails

- Check the failing request in the Network tab. If the `OPTIONS` request returns 404, 401, or 405, your router or auth layer blocks it. Let `OPTIONS` pass before authentication runs.
- If the API returns a 500 error, the error response often has no CORS headers. The browser then shows a CORS error. Check the server logs for the real error.
- If a redirect happens, such as HTTP to HTTPS or a missing trailing slash, the CORS check can fail. Call the final URL directly.
- If you use nginx, a load balancer, or an API gateway, it can remove or duplicate the headers. Set the headers in only one layer. A duplicate `Access-Control-Allow-Origin` value also causes an error.
- Do not use `mode: 'no-cors'` in `fetch`. It hides the error but gives you an empty response you cannot read.

## Local development alternative

If you do not control the API, use a dev proxy. Your dev server forwards `/api` calls to the API, so the browser sees one origin. In Vite, set `server.proxy`. In Create React App, set `"proxy"` in `package.json`. This works only in development. Production still needs CORS headers or a reverse proxy on the same origin.

If you share your server framework and the exact error text, I can give you the exact fix.
