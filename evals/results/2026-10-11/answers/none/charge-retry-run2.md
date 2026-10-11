Yes, it can, unless every retry reuses the same idempotency key. I haven't looked at your code, so I can't say whether yours does.

**Why it can happen:** a network error like a timeout or dropped connection doesn't tell you whether Stripe processed the request. If the charge went through but the response was lost, a plain retry creates a second charge.

**The fix:** send an `Idempotency-Key` header on the create call. If Stripe sees the same key again, it returns the original result instead of charging again. Keys are kept for at least 24 hours.

**How to check your code:**
- **Key stability:** the key must be generated once per logical payment attempt, such as the order or cart ID, and reused on every retry. If it's generated inside the retry loop, e.g. `uuid()` per request, it gives no protection.
- **No parameter changes between retries:** reusing a key with different parameters returns an error. That error is safe, but it shows the key is being reused when it shouldn't be.
- **Retries beyond 24 hours:** a retry from a queue or job after the key has expired could charge again.
- **Other retry layers:** check for retries outside the code you're looking at, such as an HTTP client, a load balancer, a queue worker, or a user double-clicking "Pay". Each one needs the same key or a server-side guard like a unique constraint on order ID.
- **SDK retries:** the official Stripe libraries can add idempotency keys automatically when you configure retries (e.g. `maxNetworkRetries`). Don't layer your own retry on top without passing an explicit key.
- **API choice:** the Charges API is legacy. PaymentIntents is the recommended path and handles the "was it already paid?" state better, since you can fetch the intent and check its status before retrying.

If you can't add keys right away, a fallback is to look up existing charges by order ID in metadata before retrying. That is racy, so treat it as a stopgap.

If you point me at the checkout code, I can check whether the key is stable across retries.
