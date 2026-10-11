Yes, it can, unless every retry carries the same idempotency key.

**Why it happens**

A network error is ambiguous. A timeout or dropped connection doesn't tell you whether Stripe received the request and charged the card. If the charge went through but the response was lost, a plain retry creates a second charge.

**The fix: idempotency keys**

Send an `Idempotency-Key` header on the create-charge call. Stripe stores the result of the first request with that key and returns the same result for any repeat, without charging again.

- **Generate the key once per logical payment attempt, then reuse it on every retry.** A key made fresh inside the retry loop does nothing. Derive it from something stable, such as the order or cart ID plus an attempt number, or store a UUID on the order before the first call.
- **Don't reuse a key for a different payment.** If the parameters differ (for example, a changed amount), Stripe returns an error.
- **Keys expire after about 24 hours.** Retries well after that window can create a new charge.
- **Concurrent retries can conflict.** If the first request is still in flight, the retry may get a 409 or lock error. Back off and retry rather than treating it as a failure.
- **Don't retry card declines (4xx errors).** Retry only on network errors, 5xx responses, and rate limits.

**Other double-charge paths**

- **SDK retries:** Stripe's official libraries can retry automatically (`maxNetworkRetries` in Node, `max_network_retries` in Python) and add idempotency keys for you. If you also have your own retry loop around them, make sure the keys line up.
- **Duplicate submits:** A double-clicked pay button or a client-side retry of your own checkout endpoint will bypass Stripe's protection if each submit generates a new key. Key on the order, not on the request.
- **Database backstop:** Add a unique constraint or "payment already attempted" state on the order. Before retrying after an ambiguous failure, you can also look up whether a charge with that order ID in its metadata already exists.

**Consider PaymentIntents**

The Charges create API is legacy. PaymentIntents give you a server-side object with state, so you can retrieve the intent after an ambiguous failure instead of guessing. They're also the path for SCA/3DS.

I didn't see any code in the working directory. If you point me at the checkout code, I can check whether the key is generated and reused correctly.
