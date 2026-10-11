**The fix goes on the server (your API), not the frontend.** The browser blocks the response because the API didn't send a header saying your frontend's origin is allowed.

## Fix by adding CORS headers

The API must respond with:

```
Access-Control-Allow-Origin: https://your-frontend.com
```

Using a framework's CORS middleware is easiest:

**Express (Node)**
```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000' }));
```

**FastAPI**
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"])
```

**Flask**
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

**Django**: install `django-cors-headers`, add it to `INSTALLED_APPS` and `MIDDLEWARE` (near the top), and set `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`.

**Spring Boot**: `@CrossOrigin(origins = "http://localhost:3000")` on the controller.

## Things that commonly trip people up

- **Preflight (OPTIONS) requests.** Custom headers (like `Authorization`, or `Content-Type: application/json`) or methods like PUT/DELETE trigger a preflight. The server must answer OPTIONS with a 2xx and include `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`. The middleware above handles this.
- **Credentials/cookies.** If you use `credentials: 'include'`, you can't use `*` as the origin. Specify the exact origin, add `Access-Control-Allow-Credentials: true`, and in the frontend send `credentials: 'include'`.
- **Error responses lack the header.** If your API crashes (500) or auth middleware rejects the request before CORS runs, you see a CORS error instead of the real one. Put the CORS middleware **first**, and check the Network tab for the actual status.
- **Redirects.** A redirect (e.g., `http` → `https`, or a missing trailing slash) on a preflight request will fail CORS. Call the final URL directly.
- **Proxy/CDN/gateway.** If you're behind nginx, API Gateway, or Cloudflare, the headers may need to be set there (or not stripped).
- **Exact origin match.** `http://localhost:3000` ≠ `http://127.0.0.1:3000` ≠ `https://localhost:3000`. Scheme, host, and port must all match.

## Dev-only alternative: proxy

If it's just local development, avoid CORS entirely by proxying API calls through your dev server (e.g., Vite `server.proxy`, CRA `"proxy"` in package.json). The browser then sees same-origin requests.

## Don't do this

Don't use `no-cors` mode in `fetch`. It doesn't fix anything; it gives you an unreadable "opaque" response. Browser extensions that disable CORS are fine for a quick test but not a real fix.

---

If you tell me your backend framework and the exact origin of your frontend, I can give you the exact config. Pasting the failing request's response headers from the Network tab helps too.
