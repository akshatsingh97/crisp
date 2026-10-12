Fix it on the API server. The server must send CORS headers, because the browser blocks the response when they are missing. Changing the frontend cannot fix this.

The browser sends an `Origin` header with the request. Your API must reply with `Access-Control-Allow-Origin` set to that origin.

**1. Add CORS to your API**

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

Flask: install `flask-cors`, then run `CORS(app, origins=["http://localhost:3000"])`.

Use your real frontend origin. An origin is the scheme, host, and port, for example `https://app.example.com`. It has no path and no trailing slash.

**2. Handle preflight requests**

The browser sends an `OPTIONS` request first when you use a method such as `PUT` or `DELETE`, a JSON `Content-Type`, or an `Authorization` header. This request must return a 2xx status with these headers:
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`

The libraries above do this for you. A manual setup often misses it.

**3. Check credentials**

If you send cookies (`credentials: 'include'`), the server must also send `Access-Control-Allow-Credentials: true`. In that case, `Access-Control-Allow-Origin` cannot be `*`. It must be the exact origin.

**4. Check the common causes if it still fails**
- The API returns an error such as 500, or a proxy or gateway blocks the request. Error responses often lack CORS headers, so the browser shows the CORS message and hides the real error. Check the Network tab for the status code.
- A redirect (for example HTTP to HTTPS) drops the headers. Call the final URL.
- A reverse proxy such as nginx or API Gateway strips or does not add the headers. Add them there, or make sure they pass through.
- The CORS middleware is registered after your routes. Register it first.

**For local development only**

You can proxy API calls through your dev server so the browser sees one origin. In Vite, set `server.proxy`. In Create React App, set `"proxy"` in `package.json`. Do not use `Access-Control-Allow-Origin: *` in production with private data.

If the fix does not work, tell me your server framework and the request headers from the Network tab. I can then give you the exact change.
