Fix it on the server: the API must send CORS (Cross-Origin Resource Sharing) headers that allow your frontend's origin. You cannot fix it from the frontend code.

**Why it happens**

The browser blocks a response when the API origin differs from the page origin. Origin means scheme, host, and port. The API must opt in with an `Access-Control-Allow-Origin` header.

**Steps**

1. Find your exact frontend origin, for example `http://localhost:3000` or `https://app.example.com`. Do not add a trailing slash.
2. Add CORS middleware to your API and allow that origin.
3. Handle preflight requests. The browser sends an `OPTIONS` request first when you use custom headers, `Authorization`, JSON content type, or methods other than GET and POST. Your API must answer it with a 2xx status and the CORS headers.
4. Restart the API and reload the frontend.

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

Django: install `django-cors-headers`, add `corsheaders` to `INSTALLED_APPS`, add `corsheaders.middleware.CorsMiddleware` at the top of `MIDDLEWARE`, and set `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`.

Raw headers, for any stack:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Warnings**

- If you send cookies or use `credentials: 'include'`, you must also send `Access-Control-Allow-Credentials: true`. In that case the origin cannot be `*`. Name the exact origin.
- Do not use `*` in production unless the API is truly public.
- Set the headers in only one place. If a proxy and the app both add them, the browser rejects duplicate values.

**If it still fails**

- Open the browser DevTools Network tab. Check that the `OPTIONS` request returns 2xx and includes the headers.
- If the API sits behind Nginx, a gateway, or a CDN, make sure it does not strip the headers or block `OPTIONS`.
- If an error response such as 401 or 500 lacks the headers, you will see the CORS error instead of the real error. Fix the CORS middleware order so it runs before auth.
- If you cannot change the API, use a dev proxy. In Vite, set `server.proxy`. In Create React App, set `"proxy"` in `package.json`. This works only in development.

If you tell me your backend framework and frontend origin, I can give the exact config.
