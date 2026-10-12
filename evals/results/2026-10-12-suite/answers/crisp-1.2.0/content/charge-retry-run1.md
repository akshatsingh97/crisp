Yes, if your retries do not send the same idempotency key. A network error does not tell you whether Stripe processed the request. The charge can succeed while the response is lost, and a plain retry then creates a second charge.

**Fix**

1. Generate one `Idempotency-Key` per logical payment, such as per order or per checkout attempt. Use a V4 UUID or a key derived from the order ID.
2. Save the key before the first API call.
3. Send the same key on every retry of that payment. Do not generate a new key inside the retry loop.

Stripe stores the result of the first request for that key. A retry with the same key returns the saved result and does not create a new charge. This includes saved 500 errors.

**Limits**

- Keys expire after at least 24 hours. Do not retry with an old key after that.
- Keys can be up to 255 characters.
- If you reuse a key with different parameters, Stripe returns an error.
- Stripe only saves results after the request starts running. If validation fails first, the key is not saved and a retry runs again.

**Also check**

- Retry only on network errors, timeouts, and 5xx responses. Do not retry card declines (4xx), because they will not change.
- If your client library supports it, enable its built-in retries. Stripe's official SDKs have `maxNetworkRetries`, which adds idempotency keys for you.
- Use one key per order, not per click. This also stops double-charges when a customer double-clicks or refreshes.
- For uncertain outcomes, confirm the state with a webhook (`charge.succeeded`) or by looking up the charge with your order ID in `metadata`.

One more point: the Charges API is a legacy API. Stripe recommends PaymentIntents, which track payment state and reduce this class of problem. They still need idempotency keys on create calls.

If you share the retry code, I can check whether the key is created and reused correctly.
