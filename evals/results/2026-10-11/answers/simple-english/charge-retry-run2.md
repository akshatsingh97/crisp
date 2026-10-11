Yes, it can double-charge customers if your retry does not send an idempotency key (a unique token that makes Stripe treat repeated requests as one). A network error does not tell you whether Stripe received the request. If Stripe processed the charge but the response was lost, your retry creates a second charge.

To prevent this, send an `Idempotency-Key` header on every create-charge call. Stripe saves the result of the first request under that key. If you send the same key again, Stripe returns the saved result and does not charge again. Stripe keeps keys for at least 24 hours.

The key must stay the same across all retries of one purchase. If your code generates a new random key inside the retry loop, each retry looks like a new request and the protection does nothing. Generate the key once, before the first attempt, and reuse it. A good source is your own order or cart ID, because it also protects against a customer who double-clicks the pay button. For example:

```
Idempotency-Key: order_8841_attempt_1
```

Two more rules apply. If you send the same key with different parameters, such as a different amount, Stripe returns an error. The key must therefore belong to one exact payment request. Also, if you use an official Stripe library, you can set its network retry option (`maxNetworkRetries` in Node, for example). The library then adds and reuses the key for you. But that only covers retries inside the library, so a retry loop that you wrote yourself still needs its own key.

If you use the older Charges API, consider moving to PaymentIntents. A PaymentIntent is one object that tracks a single payment through its states. A retry on the same PaymentIntent cannot create a second payment, which gives you a second layer of protection.

I can check your checkout code for this problem. Tell me where the Stripe call lives, because the working directory here has no project files.
