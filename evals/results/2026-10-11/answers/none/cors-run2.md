The fix goes on the **server** (your API), not the frontend. The browser blocks the response because your API didn't say your frontend's origin is allowed to read it.

## What to do

Add CORS headers to your API responses:

```
Access-Control-Allow-Origin: https://your-frontend.com
```

Pick the snippet for your stack:

**Express (Node)**
```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000' }));  // your frontend's origin
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

**Django**: install `django-cors-headers`, add it to `INSTALLED_APPS` and `MIDDLEWARE` (as high as possible, above `CommonMiddleware`), and set `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`.

**Spring Boot**: `@CrossOrigin(origins = "http://localhost:3000")` on the controller, or a global `WebMvcConfigurer`.

**nginx**
```nginx
add_header Access-Control-Allow-Origin "https://your-frontend.com" always;
```

## Things that commonly trip people up

- **Preflight (OPTIONS) requests.** If you send custom headers (such as `Authorization` or `Content-Type: application/json`) or use PUT/DELETE, the browser first sends an `OPTIONS` request. Your server must answer it with `2xx` and include `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`. Auth middleware that rejects `OPTIONS` is a frequent cause.
- **Credentials (cookies).** If you use `credentials: 'include'`, you can't use `*`. You must echo the exact origin and also send `Access-Control-Allow-Credentials: true`.
- **Origin must match exactly**: scheme, host, and port. `http://localhost:3000` is not `http://127.0.0.1:3000`, and a trailing slash makes it wrong.
- **Errors without CORS headers.** If your API returns a 500 or a proxy/gateway error (401, 404, 502), those responses often lack CORS headers, so you see the CORS error instead of the real one. Check the Network tab to see the actual status.
- **Redirects.** A redirect (for example, http to https, or a trailing-slash redirect) on a cross-origin request can cause this error.
- **Middleware order.** Register the CORS middleware before your routes.

## Dev-only alternative

If you don't control the API, proxy it through your dev server so requests are same-origin. For example, in Vite:

```js
// vite.config.js
server: { proxy: { '/api': 'http://localhost:8000' } }
```

Don't use a public "CORS proxy" for anything with real data.

If it still fails, tell me your backend framework and paste the failing request's status and response headers from the Network tab. I can pinpoint it.
