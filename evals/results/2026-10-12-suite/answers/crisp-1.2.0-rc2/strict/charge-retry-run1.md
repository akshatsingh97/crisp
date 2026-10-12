Yes, if your retry sends the same create-charge request without an idempotency key. An idempotency key is a unique value that lets Stripe recognize a repeated request.

**Why it happens**

A network error does not tell you whether Stripe received the request. The charge can succeed on Stripe's side while the response is lost. A retry without a key then creates a second charge.

**How to prevent it**

1. Generate one key for each logical payment attempt. Derive it from a stable value, for example the order ID or cart ID.
2. Send the key in the `Idempotency-Key` header on the first request.
3. Send the same key on every retry of that payment.
4. Create a new key only when the customer starts a new payment, for example with a different amount or card.

**Rules for keys**

- If you reuse a key with different parameters, Stripe returns an error.
- Stripe keeps the saved result for at least 24 hours. After that, a retry with the same key can create a new charge.
- If a retry arrives while the first request is still running, Stripe can return a conflict error. Wait and retry again.
- Stripe saves the result of the first request, including errors. A retry with the same key returns that same result.

**Common mistakes**

- The Stripe SDKs can add a key on their own when you set the network retry option (for example `maxNetworkRetries` in stripe-node). That covers only the SDK's internal retries. If your own code wraps the call and retries it, each attempt gets a new key unless you pass one.
- Do not generate a random key inside the retry loop. Generate it before the loop.
- A user who double-clicks the pay button can also send two requests. A key based on the order ID blocks this too.

**Extra safety**

Use webhooks, for example `charge.succeeded`, to reconcile your order records with Stripe. Stripe's newer PaymentIntents API is also built for retry-safe payment flows. It tracks one payment through its life, so a retry updates the same object. I have not seen your code, so check how your retry wrapper creates keys.
