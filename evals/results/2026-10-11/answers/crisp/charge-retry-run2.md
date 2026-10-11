Yes, it can double-charge if you retry without an idempotency key (a unique token that makes Stripe treat repeated requests as one).

A network error does not tell you whether Stripe received the request. If Stripe charged the card but the response was lost, a plain retry creates a second charge.

To prevent this:

1. Send an `Idempotency-Key` header on every create-charge call.
2. Generate the key once per order or checkout attempt, for example from the order ID. Store it before the first call.
3. Reuse the same key on every retry of that attempt. Stripe then returns the original result and does not charge again.
4. Never generate a new random key inside the retry loop. This is the most common mistake and it removes all protection.

Some limits apply:

- Stripe keeps keys for at least 24 hours. Do not reuse a key after that window for the same attempt.
- If you reuse a key with different parameters, Stripe returns an error.
- A user who clicks "Pay" twice can still create two charges if each click makes a new key. Tie the key to the order, not to the click.
- If you use the Stripe SDK, check its automatic retry setting. Recent SDKs add idempotency keys for their own retries, but not for retries in your code.

I have not seen your code. If you point me to the checkout file, I can check whether the key is stable across retries.
