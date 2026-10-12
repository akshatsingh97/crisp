Yes, if your retry sends the request again without an idempotency key (a unique ID that lets Stripe detect duplicate requests).

A network error does not prove that the charge failed. The request can reach Stripe and succeed, and then the response can get lost. A retry without a key then creates a second charge.

To prevent this:

1. Generate one unique key for each checkout attempt, for example from your order ID or a UUID saved with the order.
2. Send the key in the `Idempotency-Key` header on the first call.
3. Send the same key on every retry of that attempt.
4. Do not reuse a key for a different purchase.

Stripe returns the saved result of the first request when it sees a repeated key. If you resend a key with different parameters, Stripe returns an error.

Stripe removes keys after at least 24 hours. A retry that comes later than that can create a new charge.

Also check these points:

- Do not generate the key inside the retry loop. A new key for each retry gives no protection.
- Some Stripe SDKs can retry for you and add keys. In stripe-node, set `maxNetworkRetries`. Do not add a second retry layer on top without keys.
- Stripe recommends PaymentIntents over the older Charges API. PaymentIntents track payment state, and you can fetch the intent after an error to see if it succeeded.

I have not seen your code. If you share the checkout code, I can check where the key is made and sent.
