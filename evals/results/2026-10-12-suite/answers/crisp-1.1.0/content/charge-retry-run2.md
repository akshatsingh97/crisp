Yes, if your retry sends the request without an idempotency key (a unique value that makes repeated requests act as one). I have not read your code, so I cannot say whether you already send one.

A network error does not tell you whether Stripe received the request. If the first charge succeeded but the response was lost, a plain retry creates a second charge.

To fix it:

1. Generate one idempotency key per checkout attempt, for example from the order ID. Save it before the first call.
2. Send it in the `Idempotency-Key` header on the first call and on every retry.
3. Reuse the same key and the same parameters on each retry. Stripe then returns the saved result of the first request and does not charge again.

Watch for these risks:

- A key generated inside the retry loop gives each retry a new key. That removes the protection.
- Stripe returns an error if you reuse a key with different parameters.
- Stripe can remove keys after 24 hours, so do not retry later than that with the same key.
- If you use the official Stripe library, its `maxNetworkRetries` setting adds keys for you. Check that your own retry loop does not run on top of it.
- Stripe now recommends PaymentIntents over the older Charges API. PaymentIntents also give you a stable object to look up after an error.

If you want, I can check your checkout code for where the key is created.
