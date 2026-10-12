Yes, it can double-charge if the retry does not send the same Idempotency-Key header as the first attempt. I have not seen your code, so check that first.

**Why it happens**

A network error does not tell you whether Stripe received the request. Stripe may have created the charge, and the response may have been lost. A blind retry then creates a second charge.

**The fix**

1. Generate one idempotency key for each logical payment, not for each HTTP attempt. Use an order ID or a UUID saved with the order before the first call.
2. Send it in the `Idempotency-Key` header on the first request and on every retry.
3. Reuse the same key only with the same request parameters. Stripe returns an error if the parameters differ.

**How Stripe handles a repeated key**

- Stripe saves the status code and body of the first request, including errors with a 500 status.
- A retry with the same key returns that saved result and creates no new charge.
- Stripe can remove keys after 24 hours. Do not rely on a key for retries that happen days later.
- If the first request is still running, a retry can fail with a conflict error. Wait and retry again.

**Check your setup**

- If you use an official Stripe SDK, set its automatic retry option, for example `maxNetworkRetries` in stripe-node. The SDK then reuses one generated key across its own retries.
- If your own code wraps the call in a retry loop, make sure the key is created outside the loop.
- If the key is a new random value on each attempt, the protection does not work.

**Extra safeguards**

- Add a unique constraint in your database on the order ID and payment record, so two charges cannot be recorded for one order.
- Store your order ID in the charge metadata. After an unknown failure, you can search for an existing charge before you retry.
- Use webhooks as the source of truth for payment status.
- Stripe recommends the PaymentIntents API over the older Charges API for new work. It adds a state machine that also helps prevent duplicate payments.
