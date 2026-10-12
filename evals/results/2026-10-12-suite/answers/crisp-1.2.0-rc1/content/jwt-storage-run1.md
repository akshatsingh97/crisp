It is acceptable only if you accept the XSS risk. XSS (cross-site scripting) means attacker JavaScript runs on your page. Most security guidance advises against localStorage for tokens.

## Why it is risky

- Any script on your page can read localStorage. That includes your code, npm dependencies, analytics scripts, and injected XSS payloads.
- A stolen JWT works from the attacker's machine until it expires. The victim does not need to be online.
- localStorage has no expiry, no HttpOnly flag, and no origin rules beyond the same origin.

## Better option

Store the token in a cookie with these flags:

- `HttpOnly`: JavaScript cannot read the cookie, so XSS cannot copy the token.
- `Secure`: the browser sends the cookie over HTTPS only.
- `SameSite=Lax` or `Strict`: the browser blocks most cross-site requests that carry the cookie.

Cookies bring CSRF (cross-site request forgery) risk. SameSite covers most cases. For state-changing requests, add a CSRF token or check the `Origin` header.

HttpOnly does not stop everything. XSS can still send requests as the user while the page is open. It only stops the attacker from taking the token away.

## Common pattern for SPAs

1. Keep a short-lived access token (5 to 15 minutes) in JavaScript memory only.
2. Keep a refresh token in an HttpOnly, Secure, SameSite cookie scoped to the refresh endpoint.
3. On page load, call the refresh endpoint to get a new access token.
4. Rotate refresh tokens on each use. Revoke the whole token family if an old one is reused.

A stricter option is the BFF (backend for frontend) pattern. A small server holds the tokens and gives the browser only a session cookie. The browser never sees a JWT.

## If you must use localStorage

- Set a strict CSP (Content Security Policy) with no `unsafe-inline` scripts.
- Avoid `innerHTML` and `dangerouslySetInnerHTML`. Sanitize any HTML with DOMPurify.
- Limit third-party scripts and pin dependency versions.
- Use short token lifetimes and server-side revocation.
- Consider Trusted Types if you target Chromium browsers.

These steps reduce the risk. They do not remove it.
