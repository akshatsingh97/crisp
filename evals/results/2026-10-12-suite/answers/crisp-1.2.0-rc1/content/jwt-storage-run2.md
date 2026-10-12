It is acceptable only if you accept that any XSS bug will let an attacker steal the token. For most apps, an httpOnly cookie is the safer choice.

## Why localStorage is risky

- Any JavaScript on your page can read localStorage. This includes your code, npm dependencies, and third-party scripts.
- XSS (cross-site scripting, where an attacker runs script in your page) lets an attacker copy the JWT.
- The attacker can then use the token from their own machine until it expires.
- localStorage has no expiry and no per-request scoping. The token stays there until you remove it.

## Safer options

1. **httpOnly cookie.** Set `HttpOnly; Secure; SameSite=Lax` (or `Strict`). JavaScript cannot read the cookie, so XSS cannot copy it. You must add CSRF (cross-site request forgery) protection, such as a CSRF token or a strict SameSite setting.
2. **Short-lived access token in memory, refresh token in an httpOnly cookie.** Keep the access token in a JavaScript variable with a 5 to 15 minute life. Call a refresh endpoint on page load and when the token expires. This is a common SPA pattern.
3. **BFF (backend for frontend).** A small server holds the tokens and gives the browser only a session cookie. This is the strongest option for sensitive apps.

## Limits of these options

- XSS can still send requests as the logged-in user while the page is open. Cookies stop token theft, not all abuse.
- In-memory tokens are lost on page reload, so you need the refresh flow.
- A cookie works best when your API is on the same site. Cross-site APIs need extra CORS and cookie settings.

## If you keep localStorage

- Use short token expiry, and rotate refresh tokens if you have them.
- Set a strict CSP (Content Security Policy) header and avoid inline scripts.
- Never use `innerHTML` or `dangerouslySetInnerHTML` with untrusted data.
- Limit third-party scripts and audit your dependencies.
- Keep tokens low-privilege. Do not use this for banking, admin, or health data.
