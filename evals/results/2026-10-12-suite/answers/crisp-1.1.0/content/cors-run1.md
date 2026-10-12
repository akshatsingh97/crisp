Add CORS headers on your API server, not the frontend. The browser blocks the response because the server does not say your frontend origin is allowed.

**Fix on the server**

1. Pick your frontend origin, for example `http://localhost:3000` or `https://app.example.com`.
2. Send the header `Access-Control-Allow-Origin: <that origin>` on every API response.
3. Answer `OPTIONS` requests (preflight, the browser's permission check before some requests) with status 204. Include these headers:
   - `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
   - `Access-Control-Allow-Headers: Content-Type, Authorization`
4. If you send cookies, add `Access-Control-Allow-Credentials: true` and set `credentials: 'include'` in the frontend call. In this case the origin must be exact. `*` does not work.

**Examples**

Express (Node):
```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000', credentials: true }));
```

FastAPI (Python):
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
```

Register the CORS middleware before your routes. Otherwise some responses will not get the headers.

**Common mistakes**

- Do not use `Access-Control-Allow-Origin: *` in production if the API uses cookies or private data.
- If a proxy or gateway (nginx, API Gateway) sits in front, it can strip or skip the headers. Add them there too.
- If the API returns a 4xx or 5xx error, the error response can lack the headers. The browser then shows the same CORS message. Check the real status in the Network tab.
- For local development only, you can use a dev-server proxy (for example Vite or webpack `proxy`). This avoids CORS because the browser sees one origin.

If you tell me your server framework, I can give exact code.
