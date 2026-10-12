It is common, but it is not the safest choice. Any XSS (cross-site scripting, where an attacker runs script in your page) can read localStorage and steal the token.

**Why it is risky**
- Any JavaScript on your page can read localStorage. That includes your code, npm dependencies, and third-party scripts.
- An attacker can send a stolen token from their own machine. The token stays valid until it expires.
- localStorage has no expiry and no access controls.

**Safer option**
1. Store the token in a cookie with the `HttpOnly`, `Secure`, and `SameSite=Lax` (or `Strict`) flags. JavaScript cannot read an HttpOnly cookie.
2. Add CSRF (cross-site request forgery) protection. Cookies are sent automatically, so `SameSite` plus a CSRF token on state-changing requests is the usual defense.
3. Keep the access token short-lived, for example 5 to 15 minutes. Rotate the refresh token on each use.

An HttpOnly cookie does not stop XSS. An attacker can still send requests from the victim's browser during the attack. The cookie only stops the attacker from taking the token away.

**If you must use localStorage**
- Set a strict Content-Security-Policy (CSP) to limit which scripts can run.
- Never render untrusted HTML. Avoid `dangerouslySetInnerHTML` and `innerHTML`.
- Audit dependencies and limit third-party scripts.
- Use short token lifetimes and support server-side revocation.

**Other options**
- Use a BFF (backend-for-frontend). The server holds the tokens and gives the browser only a session cookie. This is the pattern current OAuth guidance for browser apps recommends.
- Keep the access token only in memory (a JS variable). Get a new one from an HttpOnly refresh cookie on page load. This loses the token on refresh but limits exposure.

If your app handles sensitive data, payments, or admin actions, use cookies or a BFF. For a low-risk app with strict CSP and few dependencies, localStorage is an accepted tradeoff.
