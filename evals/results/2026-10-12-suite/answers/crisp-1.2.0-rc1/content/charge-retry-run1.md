Yes, it can double-charge if each retry does not send the same Stripe idempotency key (a unique value that makes repeat requests safe). A network error often means Stripe received and processed the request, but your client never saw the response. A retry without a key then creates a second charge.

**How to fix it**

1. Generate one key per checkout attempt, before the first call. Use a UUID, or derive it from your order ID.
2. Send it in the `Idempotency-Key` header on the first request and on every retry.
3. Store the key with the order, so a restart or a second worker reuses it.

Stripe saves the result of the first request for that key, including errors. A retry with the same key returns the saved result and does not create a new charge.

**Mistakes that still cause double charges**

- A new random key on each retry. This gives no protection.
- A new key when the user clicks "Pay" again. Tie the key to the order or cart, not to the click.
- A key made only in memory. A crash between attempts loses it.

**Other behavior to know**

- Stripe can delete keys after 24 hours. Do not use retries that run later than that.
- Reusing a key with different parameters returns an error. This is a safety check.
- If a retry arrives while the first request still runs, Stripe can return a conflict error. Wait and retry again.
- The official Stripe SDKs add keys automatically when you set `maxNetworkRetries`. Check this if you use the SDK retry option instead of your own loop.

**Backup protection**

- Webhooks: handle `charge.succeeded` or `payment_intent.succeeded`, and mark the order paid from the event. This covers cases where your client never learned the result.
- Order state: before you retry, check that the order is not already paid.
- Reconciliation: for an unknown outcome, look up the charge by `metadata` (store your order ID there) before you create a new one.

Stripe now recommends PaymentIntents over the older Charges API. PaymentIntents track one payment through its states, which makes duplicates harder to create.

I have not seen your code. If you point me to the checkout and retry code, I can check how it builds and reuses keys.
