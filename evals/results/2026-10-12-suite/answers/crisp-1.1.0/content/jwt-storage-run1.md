It is acceptable only if you accept the risk that any XSS (cross-site scripting, where attacker code runs on your page) can steal the token. A stolen token works from the attacker's own machine until it expires.

Any JavaScript on your page can read localStorage. This includes a compromised npm package, a third-party script, or an injected script.

A safer default is to keep the token out of JavaScript:

1. Store the session token in a cookie with the `HttpOnly`, `Secure`, and `SameSite=Lax` (or `Strict`) flags. Scripts cannot read it.
2. Add CSRF (cross-site request forgery) protection if you use cookies. `SameSite` covers most cases. A CSRF token adds defense.
3. For a design with an access token and a refresh token, keep the short-lived access token in memory only. Keep the refresh token in an `HttpOnly` cookie.

An HttpOnly cookie does not stop XSS completely. An attacker can still send requests as the user while the script runs. It only stops token theft.

If you must use localStorage, reduce the risk:

- Set a short expiry, such as 5 to 15 minutes.
- Add a strict Content Security Policy that blocks inline scripts and unknown origins.
- Limit third-party scripts and pin dependency versions.
- Escape or sanitize all user content, and avoid `innerHTML` and `dangerouslySetInnerHTML`.
- Support server-side token revocation.

For a low-risk app with no sensitive data, localStorage is a common tradeoff. For anything with payments, personal data, or admin access, use the cookie approach.
