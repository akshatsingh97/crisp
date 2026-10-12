Add the CORS headers on your API server. The browser blocks the response because the server does not send `Access-Control-Allow-Origin`. You cannot fix this from the frontend.

CORS (Cross-Origin Resource Sharing) is a browser rule. It lets a server say which other origins may read its responses.

**Steps**

1. Find your frontend origin, for example `http://localhost:3000`. An origin is scheme, host, and port.
2. Add CORS handling to the API. Allow that origin, not `*`, if you send cookies or auth headers.
3. Answer preflight requests. The browser sends an `OPTIONS` request first for non-simple requests. Examples are JSON `POST`, `PUT`, `DELETE`, or any custom header like `Authorization`. Return status 200 or 204 with the headers below.
4. Reload and check the Network tab. The response must show `Access-Control-Allow-Origin`.

**Headers the server must send**

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

Send `Allow-Credentials` only if you use cookies. Do not combine it with `Allow-Origin: *`. The browser rejects that pair.

**Examples**

Express (Node):
```js
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:3000', credentials: true }));
```
Register this before your routes.

FastAPI (Python):
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])
```

Django: install `django-cors-headers`. Add `corsheaders` to `INSTALLED_APPS`. Add `corsheaders.middleware.CorsMiddleware` high in `MIDDLEWARE`. Set `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`.

**If it still fails**

- Check that the error is not hiding a server crash. A 500 response often lacks CORS headers. Read the server logs.
- Check the preflight in the Network tab. If `OPTIONS` returns 404 or 405, the route or a proxy blocks it.
- If a reverse proxy such as nginx sits in front, add the headers there or let the app set them. Do not set them in both places. Duplicate values cause errors.
- If the URL redirects, the redirect response needs the headers too.
- Check that the origin matches exactly. `http://localhost:3000` and `http://127.0.0.1:3000` differ.

**Development shortcut**

Use a dev proxy so the browser sees one origin. In Vite, set `server.proxy`. In Create React App, set `"proxy"` in `package.json`. Do not use this as the production fix.

**Warning**

Do not use `Access-Control-Allow-Origin: *` on APIs with private data. Allow only the origins you trust.

If you share your server framework and the exact request, I can give the exact config.
