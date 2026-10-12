Not ideal. Any XSS on your site, including one in a third-party script, can read `localStorage` and steal the token. The attacker can then use it from their own machine until it expires.

If the risk is acceptable, the rules are:

- **Use short expiry.** Give the access token 5 to 15 minutes.
- **Keep the refresh token out of JavaScript.** Store it in an `HttpOnly; Secure; SameSite` cookie.
- **Reduce XSS exposure.** Use a strict Content Security Policy, avoid `dangerouslySetInnerHTML` and `innerHTML`, and limit third-party scripts.

The safer option is to keep the token out of JavaScript entirely. Have your server set the session or JWT in an `HttpOnly; Secure; SameSite=Lax` cookie. XSS cannot read that cookie, but it can still make requests as the user while the page is open. Cookies also need CSRF protection. `SameSite` helps, and you can add a CSRF token for state-changing requests.

If you use a separate API domain, a cookie-based setup needs CORS with credentials. A backend-for-frontend (BFF) that holds the tokens server-side avoids this.

`localStorage` is acceptable for a low-risk app, such as an internal tool or a prototype. For anything with sensitive data, payments, or admin roles, use the cookie approach.
