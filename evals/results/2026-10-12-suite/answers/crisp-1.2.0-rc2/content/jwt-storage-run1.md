It works, but only if you accept that any XSS bug (cross-site scripting, where an attacker runs script in your page) will let an attacker steal the token. For most sensitive apps, an httpOnly cookie is safer.

**Why localStorage is risky**
- Any JavaScript on your page can read localStorage. This includes your own code, npm dependencies, and third-party scripts.
- One XSS bug or one compromised dependency lets an attacker copy the token. They can then use it from their own machine until it expires.
- localStorage has no expiry and no access protection. The token stays after the tab closes.

**Safer option: httpOnly cookie**
- JavaScript cannot read an httpOnly cookie, so XSS cannot copy the token.
- Set these flags: `HttpOnly; Secure; SameSite=Lax` (or `Strict`).
- Cookies add CSRF risk (cross-site request forgery, where another site triggers requests with your cookie). `SameSite` blocks most of it. For more protection, add a CSRF token.
- XSS can still send requests as the user while the page is open. An httpOnly cookie limits the damage but does not remove XSS risk.

**If you must use localStorage**
1. Make the access token short-lived, for example 5 to 15 minutes.
2. Keep the refresh token in an httpOnly cookie, and rotate it on each use.
3. Set a strict Content Security Policy (CSP) to block inline and third-party scripts.
4. Never render untrusted HTML. Avoid `dangerouslySetInnerHTML` and `innerHTML` with user data.
5. Audit and pin dependencies, and limit third-party scripts.

**Other pattern: BFF**
A backend-for-frontend (a small server that holds tokens for your SPA) keeps the JWT on the server. The browser only gets a session cookie. This is the strongest option for high-risk apps.

**Which to pick**
- Low-risk app with a strict CSP and short-lived tokens: localStorage is acceptable.
- Banking, health, admin, or any sensitive data: use httpOnly cookies or a BFF.
