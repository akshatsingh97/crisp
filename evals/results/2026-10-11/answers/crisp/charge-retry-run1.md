Yes, if each retry sends the request without the same idempotency key. A network error can hide a charge that Stripe already completed, so a blind retry can charge twice.

An idempotency key is a unique string that tells Stripe two requests are the same operation. Send it in the `Idempotency-Key` header.

1. Create one key for each logical payment attempt, for example from the order ID or cart ID. Do not create a key for each HTTP request.
2. Send that same key on the first request and on every retry.
3. Store the key with the order before the first call, so a process restart reuses it.
4. Retry only on network errors, timeouts, and 5xx responses. Do not retry 4xx card errors with the same key, because Stripe returns the saved result.

Risks:
- If you generate a new key on each retry, the protection is gone and double charges can happen.
- Stripe keeps keys for at least 24 hours. A retry after that window can create a new charge.
- If you reuse a key with different parameters, Stripe returns an error. This is a safety check, not a bug.
- Keys do not stop a customer from submitting checkout twice with different keys. Tie the key to the order, and disable the pay button after the first click.

The official Stripe libraries can add keys for you. For example, `maxNetworkRetries` in stripe-node sets a key automatically and reuses it across its own retries. Your own retry loop around that call does not share the key, so you must set one yourself.

The Charges API is also legacy. Stripe recommends PaymentIntents, which track payment state and make duplicate payments easier to detect.

If you want, I can check your checkout code for these problems. Point me to the file.
