Yes, if the retry sends a new request without the same idempotency key. A network error does not prove that the charge failed. Stripe can create the charge and the response can get lost. The retry then creates a second charge.

Idempotency key: a unique string that makes Stripe treat repeated requests as one operation.

Fix:
1. Create one key for each logical checkout, for example from the order ID or a UUID saved with the order.
2. Save the key before the first API call, so a crash or restart reuses it.
3. Send it in the `Idempotency-Key` header on every retry of that checkout. The Stripe SDKs call this option `idempotencyKey`.
4. Do not create a new key for each retry. A new key defeats the protection.

Behavior to know:
- Stripe returns the saved result of the first request when it sees the same key again. This includes errors.
- If you reuse a key with different parameters, Stripe returns an error. Use a new key only when the order really changes.
- Stripe can remove keys after 24 hours. Do not retry the same key after that time.
- Retry only on network errors, timeouts, 409, and 5xx responses. Do not retry card declines (402).

Other risks:
- A customer can double-click or reload the page. Disable the pay button and make the server reject a second submit for the same order.
- If your SDK has automatic retries (for example `maxNetworkRetries`), it adds idempotency keys for you. Check that your own retry loop does not stack on top of it.
- To check for past duplicates, search your Stripe charges for the same customer, amount, and order metadata within a short time window.
- The Charges API is legacy. PaymentIntents are better, because one intent per order cannot be charged twice once it succeeds.

I have not seen your code, so I cannot confirm whether your retry loop sends a key. Share the checkout code and I can check it.
