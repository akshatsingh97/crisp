Yes, if your retries send no idempotency key or a new key on each attempt. A network error does not tell you whether Stripe processed the request. The charge may have succeeded while the response was lost. A blind retry then creates a second charge.

**Fix**

1. Generate one idempotency key per logical charge, such as one per order or checkout attempt. Derive it from the order ID or store it with the order.
2. Send that same key in the `Idempotency-Key` header on every retry of that charge.
3. Stripe then returns the saved result of the first request instead of charging again. This includes saved 500 errors.

**Pitfalls**

- Do not generate a new key inside the retry loop. That defeats the protection.
- If you reuse a key with different parameters, Stripe returns an error. This is correct behavior.
- Keys expire after at least 24 hours. Retries after that window can create a new charge.
- Official Stripe libraries can retry for you if you set `maxNetworkRetries`. They reuse one key across those retries. If you also wrap the call in your own loop, each outer call gets a new key unless you pass one explicitly.
- Double clicks, page refreshes, and queue redelivery also cause duplicates. A key tied to the order ID covers these too.
- Do not retry card declines. A decline is a valid answer, not a network error.

**Extra safeguards**

- Store the order ID in the charge `metadata`. After an ambiguous failure, search for an existing charge for that order before you create a new one.
- Use webhooks such as `charge.succeeded` to confirm final state.
- Consider moving to PaymentIntents. Stripe recommends them over the Charges API. One PaymentIntent per order means a retry confirms the same object instead of creating a new charge.

I have not seen your code. If you share the retry logic, I can check where the key is created.
