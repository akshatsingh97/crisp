**Short answer:** It's common and often acceptable, but it's the weaker option. Any XSS bug on your site lets an attacker read the token and use it from anywhere.

## Why localStorage is risky
- **JavaScript can read it.** A single XSS hole, or one compromised npm dependency, can exfiltrate the token.
- **The stolen token works elsewhere.** The attacker can use it from their own machine until it expires.

## The usual alternative: an HttpOnly cookie
- **JavaScript can't read it,** so XSS can't steal the token itself.
- **It needs CSRF protection.** Use `SameSite=Lax` or `Strict`, plus CSRF tokens if you need cross-site requests.
- **XSS is still dangerous.** An attacker can make requests as the user from inside the page. They just can't take the token away with them.

Set the cookie with `HttpOnly; Secure; SameSite=Lax`.

## When localStorage is defensible
- You have a strict Content Security Policy and no untrusted HTML rendering.
- Access tokens are short-lived (5–15 minutes).
- The app isn't high-stakes (no payments, no sensitive personal data).

## A better pattern
1. Keep the **access token in memory** (a JS variable), so it's gone on refresh.
2. Store a **refresh token in an HttpOnly, Secure, SameSite cookie.**
3. On page load, call a refresh endpoint to get a new access token.
4. Rotate refresh tokens on each use.

## If you stay with localStorage
- Set a strict CSP, with no `unsafe-inline` scripts.
- Sanitize all user-generated HTML (for example with DOMPurify).
- Keep tokens short-lived and have a way to revoke them.
- Audit and pin your dependencies.

**Recommendation:** If you control the backend, use HttpOnly cookies or the in-memory plus refresh-cookie pattern. If you can't, localStorage with a strong CSP and short-lived tokens is a reasonable compromise.
