It works, but it is risky. Any XSS (cross-site scripting, attacker script injected into your page) can read localStorage and steal the token.

The attacker can then use the stolen token from their own machine until it expires. A compromised npm package can do the same, because all JavaScript on your page can read localStorage.

The safer option is an HttpOnly, Secure, SameSite cookie. JavaScript cannot read it. You must then defend against CSRF (cross-site request forgery, forged requests sent from other sites). Set `SameSite=Lax` or `Strict`, and add a CSRF token if you accept cross-site requests.

If you must use localStorage, reduce the damage:

1. Make the access token short-lived, for example 5 to 15 minutes.
2. Keep the refresh token in an HttpOnly cookie, not in localStorage.
3. Set a strict Content-Security-Policy that blocks inline scripts.
4. Audit and pin your dependencies.

A common middle path keeps the access token in memory only. On page load, the app calls a refresh endpoint that uses the HttpOnly cookie to get a new token.

No option fully stops XSS. A cookie only prevents token theft, because injected script can still send requests as the user.
