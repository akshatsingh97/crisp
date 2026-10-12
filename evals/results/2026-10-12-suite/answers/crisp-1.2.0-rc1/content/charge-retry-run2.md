Yes, it can double-charge if the retry sends a new request without an idempotency key. A network error does not prove the charge failed. Stripe may have created the charge, and only the response was lost. A blind retry then creates a second charge.

**Fix**
1. Generate one idempotency key (a unique string that makes repeated requests safe) per checkout attempt. Use an order ID or a UUID saved with the order.
2. Send it in the `Idempotency-Key` header on the create-charge call.
3. Reuse the same key on every retry of that attempt. Never generate a new key inside the retry loop.
4. Stripe will then return the result of the first request instead of creating a second charge.

**Rules for keys**
- Use a new key for a new purchase attempt. If the customer changes the cart or card, the old key must not be reused.
- If you reuse a key with different parameters, Stripe returns an error. This protects you from mixing up requests.
- Stripe can remove keys after 24 hours. Do not retry with the same key after that window. Check the charge state first.
- Stripe saves the result of the first request, including errors. A retry with the same key returns that same result.

**Other risks**
- If the customer clicks Pay twice, or two server workers handle the same order, both can create charges. Derive the key from the order ID so both requests share one key.
- If your retry logic wraps more than the Stripe call, such as order creation, the key must still stay the same across all retries.
- If you cannot confirm the outcome after retries, look up the charge before you create a new one. Search by order ID in the charge metadata, or use the Stripe dashboard.

**Recommendation**
- Consider moving to PaymentIntents. They track payment state on the Stripe side and handle card authentication such as 3D Secure. They also support idempotency keys.

If you share the checkout code, I can check whether the key is set and reused correctly.
