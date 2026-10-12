It works, but it's not the safest choice. Any XSS bug on your site can read `localStorage` and steal the token.

**Why it's risky**
- Any JavaScript on your page can read `localStorage`. That includes your code, npm dependencies, analytics scripts, and injected scripts.
- An attacker who steals the JWT can use it from their own machine until it expires.

**What's safer**
- **HttpOnly, Secure, SameSite cookie.** JavaScript can't read it, so XSS can't exfiltrate the token. It does expose you to CSRF, which `SameSite=Lax` or `Strict` mostly handles. Add CSRF tokens for sensitive actions. This is the usual recommendation.
- **Short-lived access token in memory, plus a refresh token in an HttpOnly cookie.** The access token lives in a JS variable, so it's gone on reload. You get a new one by calling a refresh endpoint. This is a common SPA pattern.
- **Backend-for-frontend (BFF).** The server holds the tokens and gives the browser only a session cookie. It's the strongest option but needs more infrastructure.

**When localStorage is acceptable**
- Low-risk apps, internal tools, or prototypes.
- You have a strict Content Security Policy, tightly controlled dependencies, and short token lifetimes (around 5–15 minutes).

**If you do use it**
- Keep expiry short.
- Never store long-lived refresh tokens there.
- Set a strict CSP, with no `unsafe-inline` scripts.
- Sanitize any user-generated HTML.
- Be able to revoke tokens server-side.

Cookies don't remove XSS. An attacker can still make requests as the user from inside the page. But they can't take the token with them, which limits the damage.

I can sketch the cookie and refresh flow for your stack if that helps. What backend are you using?
