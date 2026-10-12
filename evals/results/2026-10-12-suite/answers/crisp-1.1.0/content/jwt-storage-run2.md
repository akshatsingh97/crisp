Yes, only if you accept that any XSS (cross-site scripting, where attacker code runs in your page) can steal the token. Any JavaScript on your page can read localStorage. That includes your code, npm dependencies, and third-party scripts. A thief can copy the token and use it from another machine until it expires.

A safer option is to store the token in a cookie with these flags:
- `HttpOnly`: JavaScript cannot read the cookie.
- `Secure`: the browser sends the cookie only over HTTPS.
- `SameSite=Lax` or `Strict`: limits cross-site requests.

Cookies add CSRF risk (cross-site request forgery, where another site triggers requests with your cookie). The `SameSite` flag and a CSRF token reduce it. `HttpOnly` does not stop XSS from sending requests as the user, but the attacker cannot take the token away.

If you must keep the token in localStorage, reduce the damage:
1. Make access tokens short-lived, for example 5 to 15 minutes.
2. Keep the refresh token in an `HttpOnly` cookie.
3. Set a strict Content Security Policy (a header that limits which scripts can run).
4. Escape all user content and avoid raw HTML injection.
5. Audit your dependencies often.
