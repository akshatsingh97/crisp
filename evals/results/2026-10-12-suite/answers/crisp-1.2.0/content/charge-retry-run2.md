Yes, if your retries do not send the same idempotency key. An idempotency key is a unique value that lets Stripe recognize a repeated request.

A network error does not tell you whether Stripe received the request. Stripe can charge the card, and then the response can get lost on the way back. Your retry then creates a second charge.

To fix this:

1. Generate one key per logical checkout attempt, such as an order ID or a stored UUID. Do not generate a new key per HTTP request.
2. Save the key before the first call, so a crash and restart reuses it.
3. Send it in the `Idempotency-Key` header. In stripe-node, pass `{ idempotencyKey }` as a request option.
4. Reuse the exact same key and the same parameters on every retry.

Stripe stores the result of the first request for that key. A retry returns the saved result and creates no new charge. Stripe can remove keys after 24 hours, so retry within that window.

Watch for these risks:

- If you reuse a key with different parameters, Stripe returns an error.
- If you reuse one key across different orders, the second customer gets the first customer's result.
- Some Stripe SDKs add keys automatically when you set `maxNetworkRetries`. Check your SDK version before you rely on it. Your own retry loop around the SDK does not get this protection.

If you cannot confirm that a past retry was safe, search Stripe for duplicate charges. Match charges with the same customer, amount, and order metadata within a short time.

The Charges API is legacy. PaymentIntents is the recommended replacement. It tracks one payment per intent, which makes duplicates harder to create.
