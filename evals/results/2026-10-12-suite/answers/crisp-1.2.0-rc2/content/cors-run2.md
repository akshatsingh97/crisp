Fix it on the API server, not the frontend. The server must send CORS (Cross-Origin Resource Sharing) headers that allow your frontend origin.

The browser blocks the response because your API does not say the frontend origin is allowed. The request often reaches the server. The browser only hides the result.

1. Find the exact frontend origin: scheme, host, and port. Example: `http://localhost:3000`. Trailing slashes and a different port count as a different origin.
2. Add CORS to the API. Examples:

   Express (Node):
   ```js
   const cors = require('cors');
   app.use(cors({ origin: 'http://localhost:3000' }));
   ```

   FastAPI (Python):
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["*"], allow_headers=["*"])
   ```

   Any other server: send these headers on responses:
   ```
   Access-Control-Allow-Origin: http://localhost:3000
   ```
3. Register the CORS middleware before your routes. If it comes after, routes will not send the headers.
4. Restart the API and reload the frontend. Check the Network tab for `Access-Control-Allow-Origin` in the response headers.

Handle preflight requests if you send JSON, custom headers such as `Authorization`, or methods like PUT and DELETE. The browser first sends an `OPTIONS` request. Your server must answer it with a 2xx status and these headers:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

If you send cookies or use `credentials: 'include'`, you must also send `Access-Control-Allow-Credentials: true`. In that case the origin cannot be `*`. It must be the exact origin.

Do not use `Access-Control-Allow-Origin: *` in production for private APIs. It lets any website read the responses.

If the error persists:
- Check that the API is not returning an error page, such as a 404, 500, or a proxy error. Those responses often lack CORS headers, which causes the same message.
- Check that a gateway or reverse proxy (nginx, API Gateway, Cloudflare) does not strip or override the headers.
- Check that a redirect (for example, HTTP to HTTPS) is not breaking the preflight. Preflight requests must not redirect.

For local development only, you can avoid CORS with a dev proxy. In Vite, set `server.proxy`. In Create React App, set `"proxy"` in `package.json`. The browser then sees same-origin requests.

If you cannot change the API, put your own backend or proxy between the frontend and that API. CORS applies only to browsers, so server-to-server calls work.
