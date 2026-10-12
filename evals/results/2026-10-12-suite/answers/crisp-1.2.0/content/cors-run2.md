Fix it on the API server: send CORS headers that allow your frontend's origin. The browser blocks the response because the server does not send `Access-Control-Allow-Origin`. Changing the frontend code cannot fix this.

CORS (Cross-Origin Resource Sharing) is a browser rule. It blocks a page from reading responses from a different origin. An origin is the scheme, host, and port together.

**Steps**

1. Find the exact origin of your frontend, for example `http://localhost:3000`.
2. Add CORS support to your API with that origin allowed.
3. Handle preflight requests. The browser sends an `OPTIONS` request first if you use custom headers, `Authorization`, JSON content type, or methods like `PUT` and `DELETE`. The server must answer it with a 2xx status and the CORS headers.
4. Restart the API and reload the page.

**Examples**

Express (Node):
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

Any other server: return these headers on the response and on the `OPTIONS` response:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Warnings**

- If you send cookies or use `credentials: 'include'`, you must set `Access-Control-Allow-Credentials: true`. You must also name the exact origin. The value `*` does not work with credentials.
- Do not use `*` in production for APIs that need authentication.
- Add the CORS middleware before your routes. If it runs after them, the headers will not appear.

**If it still fails**

- Open the Network tab and check the `OPTIONS` request. If it returns 404, 401, or 500, fix that first. A redirect on `OPTIONS` also breaks CORS.
- Check that the origin matches exactly. `http://localhost:3000` and `http://127.0.0.1:3000` are different origins. A trailing slash in the allowed origin also causes a mismatch.
- If a proxy or gateway sits in front of your API (Nginx, API Gateway, Cloudflare), it can strip or override the headers. Configure CORS there too.
- If you cannot change the API, use a dev proxy. Examples are Vite `server.proxy` or the Create React App `proxy` field. The browser then sees a same-origin request. This works for development only.

If you tell me your backend framework and frontend origin, I can give exact code.
