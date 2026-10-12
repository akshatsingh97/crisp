**It's common, but it's not the safest option.** The main risk is XSS. Any JavaScript that runs on your page can read `localStorage` and steal the token. That includes an injected script, a compromised npm dependency, or a malicious third-party script like an analytics or ad tag. A stolen token can be used from the attacker's own machine until it expires.

**Safer default: an HttpOnly cookie**
- Set the cookie with `HttpOnly; Secure; SameSite=Lax` (or `Strict`).
- JavaScript can't read it, so XSS can't exfiltrate it.
- XSS can still make requests as the user while the page is open, but the attacker can't take the token away.
- Cookies bring CSRF risk. `SameSite` covers most of it. For state-changing requests, add a CSRF token or check the `Origin` header.

**If you must use `localStorage`, reduce the damage:**
- Use short-lived access tokens, 5–15 minutes.
- Put the refresh token in an HttpOnly cookie, and rotate it on every use.
- Set a strict Content-Security-Policy (no `unsafe-inline`, a tight `script-src`).
- Keep third-party scripts to a minimum, and pin and audit your dependencies.
- Sanitize anything you render as HTML. Most frameworks escape by default, so avoid `dangerouslySetInnerHTML` and `v-html`.

**Best pattern for many SPAs**
- Keep the access token in memory only (a JS variable). It disappears on refresh.
- Get a new one on load from a refresh endpoint that uses an HttpOnly cookie.
- For high-security apps, use a backend-for-frontend (BFF). The server holds the tokens and the browser only gets a session cookie.

**When `localStorage` is acceptable**
- Low-sensitivity apps, internal tools, or prototypes with short-lived tokens, a strict CSP, and few dependencies.
- It's a poor choice for banking, healthcare, admin panels, or anything where one stolen token would be costly.

If you tell me your stack (who issues the JWT, whether the API is same-origin), I can suggest a specific setup.
