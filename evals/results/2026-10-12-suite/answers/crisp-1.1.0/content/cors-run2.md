Fix it on the API server. Add CORS headers (rules that let a browser call a different origin) to the API responses. The frontend cannot fix this.

The browser blocks the call because the API origin differs from the page origin. An origin is the scheme, host, and port. The API must reply with `Access-Control-Allow-Origin` set to your frontend origin.

1. Find the exact frontend origin, for example `http://localhost:3000`. Do not add a trailing slash.
2. Enable CORS in your API. Express example:

   ```js
   const cors = require("cors");
   app.use(cors({
     origin: "http://localhost:3000",
     methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allowedHeaders: ["Content-Type", "Authorization"],
   }));
   ```

   FastAPI example:

   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Add the CORS middleware before your routes. Otherwise the headers will not reach every response.
4. Restart the API. In the browser Network tab, check that the response has `Access-Control-Allow-Origin`.

The browser sends a preflight request (an `OPTIONS` check before the real call) when you use JSON, custom headers, or methods like PUT. The server must answer it with a 2xx status and the CORS headers. Middleware usually does this for you.

- If you send cookies, set `credentials: "include"` in the frontend and `Access-Control-Allow-Credentials: true` on the server. The origin cannot be `*` in that case.
- If a proxy, gateway, or CDN sits in front of the API, set the headers there too. Redirects and error responses (401, 500) must also carry the headers.
- For local development only, you can use a dev-server proxy, such as Vite `server.proxy`. The browser then sees one origin.

If this does not fix it, send your server framework and the failing request and response headers.
