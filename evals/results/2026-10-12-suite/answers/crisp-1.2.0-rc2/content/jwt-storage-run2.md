It is acceptable only if you accept the XSS risk (cross-site scripting, where an attacker runs script on your page). For most apps, an HttpOnly cookie is safer.

**Why localStorage is risky**
- Any JavaScript on your page can read localStorage. One XSS bug lets an attacker steal the token.
- Third-party scripts and npm dependencies run with full access. A compromised package can read the token.
- The attacker can use a stolen token from their own machine until it expires.

**Why cookies are safer**
- JavaScript cannot read an HttpOnly cookie, so XSS cannot steal the token.
- XSS can still send requests as the user while the page is open. HttpOnly limits the damage but does not remove it.
- Cookies need CSRF (cross-site request forgery) protection. Set `SameSite=Lax` or `Strict`. Add a CSRF token if you need `SameSite=None`.

**Recommended setup**
1. Set the token in a cookie with `HttpOnly; Secure; SameSite=Lax` (or `Strict`).
2. Use a short-lived access token, for example 5 to 15 minutes.
3. Store a refresh token in a separate HttpOnly cookie. Limit its path to the refresh endpoint.
4. Rotate refresh tokens on each use. Revoke them on logout.
5. Add a strict Content Security Policy (CSP) to reduce XSS risk. Avoid `unsafe-inline` scripts.

**If you must use localStorage**
- Keep the token lifetime very short.
- Escape all user content. Avoid `dangerouslySetInnerHTML` and `innerHTML`.
- Audit third-party scripts and dependencies.
- Use a strict CSP.

**Alternative**
Use a backend-for-frontend (BFF). The BFF keeps tokens on the server and gives the browser only a session cookie. This is the strongest option for sensitive apps.

**Compromise**
Keep the access token in memory only (a JavaScript variable) and the refresh token in an HttpOnly cookie. XSS cannot read a stored token. The user must refresh the token after a page reload.
