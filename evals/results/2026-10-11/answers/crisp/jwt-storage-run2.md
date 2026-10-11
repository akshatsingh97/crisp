It is acceptable only if you accept the risk that any XSS flaw will let an attacker steal the token. An httpOnly cookie is safer.

XSS (cross-site scripting) means an attacker runs their own script on your page. Any script on your page can read localStorage. That includes a compromised npm package or a third-party script. The attacker can then copy the token and use it from another machine.

An httpOnly cookie cannot be read by JavaScript. This limits the damage from XSS. Cookies bring a different risk, CSRF (a forged request sent from another site). Reduce it with `SameSite=Lax` or `Strict` and, if needed, a CSRF token.

Preferred setup:

1. Send the token in a cookie with `HttpOnly`, `Secure`, and `SameSite` set.
2. Keep access tokens short-lived, for example 5 to 15 minutes.
3. Use a refresh token in an httpOnly cookie to get new access tokens.
4. Add a strict Content Security Policy (CSP) to limit which scripts can run.

If you must use localStorage, keep the access token short-lived and use a strict CSP. Avoid untrusted third-party scripts. Never store a long-lived refresh token there.
