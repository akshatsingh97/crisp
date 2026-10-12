It's common, but it carries a real risk. Any XSS vulnerability lets an attacker read the token, because JavaScript can read `localStorage`. They can then use the token from anywhere until it expires.

**Why it's risky**
- Any injected script, including one from a compromised npm dependency or third-party tag, can run `localStorage.getItem('token')` and send it out.
- The attacker keeps access after the user closes the tab, and you can't scope the stolen token to the victim's browser.

**Why people still use it**
- It's simple, and it isn't affected by CSRF because the browser doesn't attach the token automatically.
- `HttpOnly` cookies aren't a full fix either: XSS can still make authenticated requests as the user, but it can't take the credential away with it.

**Better options, most secure first**
1. **`HttpOnly`, `Secure`, `SameSite=Lax` or `Strict` cookie** set by your server. JavaScript can't read it. Add CSRF protection (`SameSite` plus a CSRF token for state-changing requests) if you use `Lax` or cross-site calls.
2. **Short-lived access token in memory only (a JS variable), plus a refresh token in an `HttpOnly` cookie.** On page load, call a refresh endpoint to get a new access token. XSS can still use the in-memory token while the page is open, but it can't steal a long-lived credential.
3. **Backend-for-frontend (BFF).** Your server holds the tokens and gives the SPA only a session cookie. This is the pattern recommended for OAuth/OIDC browser apps.

**If you do keep it in `localStorage`**
- Make access tokens short-lived (5–15 minutes).
- Set a strict Content-Security-Policy (no `unsafe-inline`, restrict script sources).
- Avoid `dangerouslySetInnerHTML` and `innerHTML`, and sanitize any user HTML with DOMPurify.
- Pin and audit dependencies, and use Subresource Integrity for any third-party scripts.
- Support server-side revocation, and rotate refresh tokens if you use them.

**Bottom line:** for a low-stakes app with a tight CSP and short token lifetimes, `localStorage` is an acceptable tradeoff. For anything handling sensitive data, payments, or admin access, use an `HttpOnly` cookie or a BFF.

If you tell me your stack and whether the API is same-site, I can suggest a concrete setup.
