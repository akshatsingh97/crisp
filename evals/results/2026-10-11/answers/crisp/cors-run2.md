Add CORS headers to your API server's responses. The browser blocks the call because the API does not say that your frontend origin is allowed.

CORS (Cross-Origin Resource Sharing) is a browser rule. A page may call another origin only if that server opts in. The fix must happen on the API, not in the frontend code.

1. Find your frontend origin exactly, for example `http://localhost:3000`. Include scheme, host, and port.
2. Add CORS middleware to the API and allow that origin.
3. Handle the preflight request. The browser sends an `OPTIONS` request first for non-simple calls, such as JSON bodies or an `Authorization` header. The server must answer it with a 2xx status and the CORS headers.
4. Restart the API and retry.

Examples:

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

Flask (Python):
```python
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000"])
```

Raw headers, for any stack:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

Risks and common mistakes:
- Do not use `*` in production for private APIs. Use an explicit list of origins.
- If you send cookies or use `credentials: 'include'`, you cannot use `*`. You must name the origin and also send `Access-Control-Allow-Credentials: true`.
- Add the CORS middleware before your routes. If it comes after, some responses will miss the headers.
- The error can also appear when the API returns a 4xx or 5xx error, or when a proxy or redirect strips the headers. Check the Network tab for the real status code.
- Do not use a browser extension that disables CORS as a fix. It only hides the problem on your machine.

If you do not control the API, use a backend proxy that you own. A dev server proxy also works, such as Vite `server.proxy` or the Create React App `proxy` setting.

If you tell me your server framework, I can give exact code.
