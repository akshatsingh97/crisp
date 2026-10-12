Yes, it can double-charge if you retry without an idempotency key. Stripe can process the first request and the response can still get lost on the network. Your retry then creates a second charge.

The fix is to send an `Idempotency-Key` header on every create-charge request.

1. Generate one key per logical payment attempt, for example from your order or cart ID. Do not generate a new key per retry.
2. Send the same key on every retry of that attempt.
3. Stripe then returns the saved result of the first request instead of charging again.

Keep these limits in mind:

- Stripe keeps keys for at least 24 hours, so do not reuse a key after that window.
- If you reuse a key with different parameters, Stripe returns an error. This protects you from mismatched retries.
- Retries of a request that failed with a 5xx error or timeout are safe with the same key.
- Stripe's official client libraries can add the key and retry for you. Check that your code does not create a new key on each retry.

I have not seen your code. If you want, point me to the checkout file and I will check whether it sets the key correctly.
