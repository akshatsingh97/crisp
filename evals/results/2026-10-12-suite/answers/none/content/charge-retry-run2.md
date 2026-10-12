**Yes, it can, unless every attempt of the same charge sends the same `Idempotency-Key` header.**

**How it happens**
1. Your server sends the charge request.
2. Stripe processes it and charges the card.
3. The response is lost (timeout or connection reset), so your code sees a network error.
4. Your code retries. Stripe has no way to know it's the same request, so it creates a second charge.

**The fix**
- Send an `Idempotency-Key` header on the create call. Stripe saves the result of the first request under that key. A retry with the same key returns the original result and doesn't charge again.
- Create the key once per logical payment, not once per attempt. Use something stable like an order ID or checkout-session ID, or a UUID stored with the order before the first call. If you generate a fresh UUID inside the retry loop, it protects nothing.
- Keys are kept for about 24 hours. Reusing a key with different parameters returns an error, which is the behavior you want.
- If you use a Stripe SDK, setting `maxNetworkRetries` makes it retry with an idempotency key automatically. That only helps if you aren't also running your own retry loop around it.

**Other things to check**
- Only retry on network errors, 5xx and 429. Don't retry card declines or other 4xx errors.
- A user double-clicking "Pay" or refreshing can cause the same duplicate. Deriving the key from the order ID covers that case too.
- `/v1/charges` is the legacy API. PaymentIntents is the recommended replacement, and it handles retries and 3D Secure better. Idempotency keys work the same way there.

If you point me at the checkout code, I can check whether the key is created once per order or inside the retry loop.
