Not ideal. Any XSS bug on your site lets an attacker read the token from `localStorage` and use it from their own machine.

**Why it is risky**
- Any JavaScript on your page can read `localStorage`. That includes your own code, npm dependencies, and third-party scripts.
- A stolen token works until it expires. The attacker does not need to stay on your site.

**What to do instead**
1. Keep the token out of JavaScript. Have the server set it in an `HttpOnly; Secure; SameSite=Lax` (or `Strict`) cookie. Scripts cannot read that cookie, so XSS cannot copy it.
2. Add CSRF protection when you use cookies. `SameSite` helps, and a CSRF token or custom header check is safer.
3. Use a short-lived access token, about 5 to 15 minutes. Pair it with a refresh token in an `HttpOnly` cookie.
4. For the strongest setup, use a backend-for-frontend (BFF). The server keeps the tokens, and the browser only holds a session cookie.

**When `localStorage` is acceptable**
- The app holds low-value data, the token lives a short time, and you have a strict Content-Security-Policy. You also need to audit your dependencies.
- You accept that an XSS bug will leak the token. Many teams still choose this for simplicity.

**Note:** An `HttpOnly` cookie does not stop XSS. An attacker can still send requests as the user while the script runs on the page. It only stops the attacker from taking the token away and reusing it later.

If you tell me your backend and how long your tokens live, I can suggest a concrete setup.
