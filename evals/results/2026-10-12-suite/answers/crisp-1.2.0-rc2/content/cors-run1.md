Fix it on the API server. The server must send an `Access-Control-Allow-Origin` header that names your frontend origin. You cannot fix it in the frontend code.

Browsers block a cross-origin response unless the server allows it. An origin is the scheme, host, and port together. `http://localhost:3000` calling `http://localhost:8000` is cross-origin.

## Steps

1. Find the exact origin of your frontend, for example `http://localhost:3000`.
2. Add CORS (Cross-Origin Resource Sharing) support to your API. Examples:

Express:
```js
const cors = require('cors');
app.use(cors({
  origin: 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

Flask:
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Any other server: send these headers on responses.
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

3. Restart the API and retry the request. The response in the browser Network tab must now show `Access-Control-Allow-Origin`.

## Preflight requests

For some requests, the browser first sends an `OPTIONS` request called a preflight. This happens with methods like `PUT` or `DELETE`, a JSON `Content-Type`, or a custom header like `Authorization`. Your server must answer `OPTIONS` with a 2xx status and the headers above. If the preflight fails, the real request never runs.

## Cookies and credentials

If you send cookies or use `credentials: 'include'`, two more rules apply:

- Set `Access-Control-Allow-Credentials: true` on the server.
- Do not use `*` as the origin. Name the exact origin.

## If it still fails

- Check that the error comes from the right URL. A proxy, load balancer, or API gateway can strip headers or return an error page without CORS headers.
- A 4xx or 5xx error response can also lack CORS headers. The CORS message then hides the real error. Test the API with `curl -i` to see the true status.
- Redirects can break CORS. Use the final URL, for example `https://` instead of `http://`, or add or remove the trailing slash.
- Make sure the CORS middleware runs before your routes.
- Do not use `mode: 'no-cors'` in `fetch`. It hides the error but gives you an unreadable response.

## If you do not control the API

- In development, use a dev server proxy. In Vite, set `server.proxy`. In Create React App, set `"proxy"` in `package.json`. The browser then sees the same origin.
- In production, call your own backend, and let that backend call the third party API.

Avoid `Access-Control-Allow-Origin: *` on APIs with private data or cookie auth. Allow only the origins you trust.

If the fix does not work, send me your server framework, the frontend URL, the API URL, and the failing request headers from the Network tab. I can then point to the exact cause.
