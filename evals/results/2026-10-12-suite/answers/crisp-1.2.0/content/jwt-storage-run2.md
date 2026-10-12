It is acceptable only if you accept that any XSS bug (cross-site scripting, attacker script running in your page) can steal the token. For anything sensitive, use an HttpOnly cookie instead.

**Why localStorage is risky**
- Any JavaScript on your page can read localStorage. This includes injected scripts, compromised npm packages, and third-party scripts.
- An attacker who steals the JWT can use it from their own machine until it expires.
- You cannot revoke a stateless JWT before it expires unless you add a server-side denylist.

**Safer options**
1. Store the token in a cookie with `HttpOnly`, `Secure`, and `SameSite=Lax` or `Strict`. JavaScript cannot read it.
2. Keep a short-lived access token in memory only. Store the refresh token in an HttpOnly cookie. The app gets a new access token after each page reload.
3. Use a backend-for-frontend (BFF). A small server holds the tokens and gives the browser only a session cookie.

**Limits of cookies**
- XSS can still send requests as the user while the page is open. HttpOnly only stops token theft.
- Cookies send automatically, so you must defend against CSRF (cross-site request forgery). Use `SameSite` and, if needed, a CSRF token.

**If you keep localStorage**
- Make the token expire quickly, for example 5 to 15 minutes.
- Set a strict Content Security Policy (CSP) to block inline and unknown scripts.
- Avoid `innerHTML` and `dangerouslySetInnerHTML` with untrusted data. Sanitize any HTML you must render.
- Limit third-party scripts and audit dependencies.
- Give the token minimal scopes.

For a low-risk app, such as a hobby project with no sensitive data, localStorage is a reasonable trade-off. For payments, personal data, or admin access, use the cookie approach.
