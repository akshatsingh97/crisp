Add CORS headers on your API server, not in the frontend. The server must send `Access-Control-Allow-Origin` with your frontend's origin.

CORS (Cross-Origin Resource Sharing) is a browser rule. It blocks a page from reading responses from a different origin unless that server allows it. An origin is the scheme, host, and port together.

1. Find your frontend origin, for example `http://localhost:3000`.
2. Add CORS handling to your API. Examples:

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

   Other servers: send these response headers:
   ```
   Access-Control-Allow-Origin: http://localhost:3000
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
   Access-Control-Allow-Headers: Content-Type, Authorization
   ```
3. Restart the API and reload the page.
4. Check the Network tab. The response must show the `Access-Control-Allow-Origin` header.

Common causes if it still fails:
- The API must also answer the `OPTIONS` preflight request (a check the browser sends first) with a 2xx status. Send the headers on that response too.
- If you send cookies or use `credentials: 'include'`, you must set `Access-Control-Allow-Credentials: true`. You cannot use `*` as the origin in that case. Name the exact origin.
- Errors such as 404 or 500 from the API often lack CORS headers. The browser then shows the CORS error and hides the real error. Check the server logs.
- A proxy or gateway in front of the API can strip the headers. Set CORS there if it does.

Do not use `*` in production if the API uses cookies or private data. During local development, a dev-server proxy (for example Vite `server.proxy`) also avoids CORS, because the browser sees one origin.
