It works, but it is not the best choice, because any script that runs on your page can read localStorage and steal the token. This kind of attack is called XSS (cross-site scripting, where an attacker gets their code to run inside your site). One vulnerable dependency or one unescaped user input can be enough. The attacker can then send the token to their own server and use it from anywhere until it expires.

The safer default is to keep the token in a cookie with the `HttpOnly`, `Secure`, and `SameSite=Lax` (or `Strict`) flags. `HttpOnly` means JavaScript cannot read the cookie, so XSS cannot copy it. `SameSite` blocks most CSRF (cross-site request forgery, where another site tricks the browser into sending your cookie). For extra safety, add a CSRF token on requests that change data.

A common pattern for a single-page app is a short-lived access token held only in memory, plus a refresh token in an `HttpOnly` cookie. The app gets a new access token from the refresh endpoint when the page loads. A page reload loses the memory copy, but the cookie restores it.

Be aware that cookies do not fix XSS. An attacker with script access can still make requests as the user while the page is open. The cookie only stops them from taking the token away and using it later.

If you choose localStorage anyway, which can be reasonable for low-risk apps, reduce the damage. Keep token lifetimes short, often 5 to 15 minutes. Set a strict Content Security Policy (a browser rule that limits which scripts can run). Avoid third-party scripts that you do not control. Never use `innerHTML` with untrusted data. Do not store long-lived refresh tokens there.
