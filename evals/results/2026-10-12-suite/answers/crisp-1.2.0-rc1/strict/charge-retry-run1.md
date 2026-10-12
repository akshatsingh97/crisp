Yes, if the retry sends the create-charge request without the same idempotency key. An idempotency key is a unique value that makes Stripe treat repeat requests as one.

**Why it happens**

A network error does not prove the charge failed. Stripe can receive the request and create the charge, then the response is lost or times out. Your code sees an error and sends the request again. Stripe sees a new request and creates a second charge.

**The fix**

1. Generate one idempotency key for each checkout attempt. Use the order ID or a UUID.
2. Store the key before the first call to Stripe.
3. Send it in the `Idempotency-Key` HTTP header on the first call and on every retry.
4. Use a new key only when the customer starts a new, different payment.

Stripe saves the result of the first request for that key. Later requests with the same key return the saved result and do not create a new charge. Stripe removes keys after at least 24 hours. A key can have up to 255 characters.

**Risks and limits**

- Do not generate a new random key on each retry. That removes the protection.
- If you reuse a key with different parameters, such as another amount, Stripe returns an error.
- If a retry arrives while the first request is still running, Stripe can return a conflict error. Wait and retry.
- Stripe saves the result of a failed request too, including some 500 errors. Retries with the same key return that same result. A request that fails validation before it runs is not saved.
- Every layer that retries needs the same key. This includes your HTTP client, queue redelivery, a gateway, and a user who double-clicks the pay button.
- Only POST requests need the key. GET and DELETE requests are already safe to repeat.

**Alternatives**

- Official Stripe libraries can retry for you. Set `maxNetworkRetries` and the library adds an idempotency key automatically. Check your library version to confirm.
- The older Charges API is the one you describe. Stripe recommends PaymentIntents for new work. You create one PaymentIntent for each order and confirm it again on retry, which will not charge twice. Still send an idempotency key when you create the PaymentIntent.
- If you cannot add keys now, search Stripe for an existing charge with the same order ID in its metadata before each retry. This is weaker, because two requests at the same time can both pass the check.

I have not seen your code. If you share the checkout and retry code, I can check whether it sends a stable key.
