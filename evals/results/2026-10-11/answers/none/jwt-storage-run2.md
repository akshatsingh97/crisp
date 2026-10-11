**It's common, but it's not the safest option.** The main risk is XSS. Any JavaScript that runs on your page can read `localStorage`, so one XSS bug, or one compromised npm dependency, lets an attacker steal the token and use it from anywhere.

**Why people still do it**
- It's simple, and it works with any API and with `Authorization: Bearer` headers.
- It isn't vulnerable to CSRF, because the browser doesn't attach it automatically.
- If an attacker has XSS, they can also act as the user from inside the page, whatever storage you use.

**Safer option: an `HttpOnly` cookie**
- JavaScript can't read it, so XSS can't exfiltrate the token.
- Set `Secure` and `SameSite=Lax` or `Strict`.
- Because cookies are sent automatically, you then need CSRF protection. `SameSite` covers most of it, and a CSRF token covers the rest.

**Best practical pattern for SPAs**
- Use a short-lived access token (5–15 minutes) kept in memory only, in a JS variable.
- Use a refresh token in an `HttpOnly`, `Secure`, `SameSite` cookie, scoped to the refresh endpoint.
- Rotate refresh tokens on each use.
- On page reload, call the refresh endpoint to get a new access token.

**If you stay with localStorage**
- Keep token lifetimes short, and add refresh and revocation.
- Set a strict Content Security Policy, with no `unsafe-inline`.
- Never inject unsanitized HTML, and avoid `dangerouslySetInnerHTML` and `innerHTML`.
- Audit your dependencies and use Subresource Integrity for third-party scripts.

**Rule of thumb:** localStorage is acceptable for low-risk apps with a strong CSP and short-lived tokens. For anything handling sensitive data, money, or admin access, use the cookie-based approach, or a backend-for-frontend (BFF) that keeps tokens server-side.

If you tell me your stack and what the app protects, I can suggest a concrete setup.
