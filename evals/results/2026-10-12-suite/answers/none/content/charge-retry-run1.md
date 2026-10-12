Yes, it can, if the retries do not send the same `Idempotency-Key` header as the first request. I have not seen your code, so this is the general rule.

**Why it happens:** A network error or timeout does not tell you if Stripe got the first request. Stripe may have charged the card and the response was lost. A plain retry then creates a second charge.

**The fix:**
- Make one idempotency key for each payment attempt. Use a UUID, or a value from your order ID.
- Save the key before the first call, and send it on every retry of that payment.
- Do not make a new key inside the retry loop. This is the most common mistake.
- Stripe returns the stored result of the first request when it sees the same key again.

**Limits to check:**
- Stripe can remove keys after 24 hours. Do not retry later than that with the same key.
- If you reuse a key with different parameters, such as a new amount, Stripe returns an error.
- Stripe stores the first result, including errors. After a card decline, a retry with the same key returns the same decline. Use a new key only when the customer starts a new attempt.
- Use an order-based key, not a per-click key. Then a double click or a repeated request from the browser does not create two charges.

**Also check:**
- The official Stripe SDKs can retry on their own and reuse the key. Set `maxNetworkRetries` in Stripe's Node, Python, Ruby, and other libraries.
- If your retries come from a queue or a job runner, make sure each retry reads the saved key.
- Stripe now recommends PaymentIntents instead of the older Charges API. PaymentIntents support the same idempotency keys.

If you share the retry code, I can check it for these problems.
