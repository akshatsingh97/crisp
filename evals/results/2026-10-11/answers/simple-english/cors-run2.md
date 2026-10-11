You fix this error on the server, not in the frontend: your API must send an `Access-Control-Allow-Origin` header that names your frontend's origin (the scheme, host, and port that the page loads from). The browser blocks the response because your frontend and your API are on different origins, and the API did not say that it allows the frontend.

If you use Express, you can add the `cors` package and list your frontend origin:

```js
const cors = require("cors");
app.use(cors({ origin: "http://localhost:3000" }));
```

Replace the origin with the real address of your frontend. In production, use your real domain. Use `origin: "*"` only for a public API that does not use cookies.

If you use another framework, send the same header yourself. For example, in Django you install `django-cors-headers`, and in FastAPI you add `CORSMiddleware`. In each case you set the allowed origin to your frontend address.

If your request sends custom headers such as `Authorization`, or uses a method such as PUT or DELETE, the browser first sends a preflight request (an OPTIONS request that asks permission). Your server must answer it with status 200 or 204 and also send `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`. Most CORS libraries do this for you when you register them before your routes.

If you send cookies, set `credentials: "include"` in the frontend request. Then the server must send `Access-Control-Allow-Credentials: true` and an exact origin, because the browser rejects `*` in that case.

If the header is still missing after these changes, check three things. First, make sure that the CORS code runs before your routes and before any code that returns early. Second, make sure that error responses also carry the header, because a 500 error without it looks like a CORS error. Third, make sure that a proxy or gateway in front of your API does not remove the header.

During local development, you can also avoid the problem with a dev proxy. Vite and Create React App both can forward `/api` calls to your backend, so the browser sees one origin. Do not fix this by disabling browser security, because that hides the problem and does not help your users.

If these steps do not solve it, tell me your server framework and the exact request that fails, and I can give you the exact code.
