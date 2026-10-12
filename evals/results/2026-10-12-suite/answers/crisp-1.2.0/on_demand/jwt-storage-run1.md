It's common, but it's a real tradeoff. Any XSS bug on your site lets an attacker read the token, because `localStorage` is readable by any JavaScript on the page. A stolen JWT works from the attacker's machine until it expires, even after the user closes the tab.

**Why people do it anyway**
- It's simple, and it survives page reloads.
- It isn't sent automatically, so it's not vulnerable to CSRF.
- A `httpOnly` cookie only protects the token from being read. An XSS attacker can still make authenticated requests from the victim's browser, so cookies don't fully fix XSS.

**When it's acceptable**
- The app is low to moderate risk, such as an internal tool or a hobby project.
- You have a strict Content-Security-Policy, you escape output properly, and you vet your third-party scripts. Supply-chain scripts are a common way in.
- Access tokens are short-lived (5 to 15 minutes).

**When to do better**
- The app handles money, health data, admin powers, or sensitive personal data.

**Safer pattern**
1. Keep the access token in memory only, in a JS variable, and accept that a reload loses it.
2. Store a refresh token in a `httpOnly; Secure; SameSite=Strict` (or `Lax`) cookie.
3. On page load, call a refresh endpoint to get a new access token.
4. Rotate refresh tokens on each use and revoke them on logout.

If your frontend and API share a site, a plain `httpOnly` session cookie with CSRF protection is often simpler and safer than JWTs.

I can sketch the refresh-token flow for your stack if you tell me what you're using.
