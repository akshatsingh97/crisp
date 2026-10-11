Yes, it can double-charge customers if the retry does not send an idempotency key (a unique token that makes Stripe treat repeated requests as one). I have not looked at your code, so this answer is about the pattern you described.

A network error does not tell you that the charge failed. Stripe may have created the charge and then lost the connection before your server received the reply. If your code sends the same request again with no key, Stripe sees a new request and creates a second charge.

To fix this, send an `Idempotency-Key` header with every create-charge call. Generate the key once for each payment attempt, and reuse the same key on every retry of that attempt. Stripe stores the result of the first request with that key. When a retry arrives with the same key, Stripe returns the stored result and does not charge again. Stripe keeps keys for at least 24 hours.

Choose the key with care. A random value created inside the retry loop is wrong, because each retry then gets a new key. A good key comes from something that is stable for the purchase, such as your order ID or cart ID. This also protects you when a customer double-clicks the pay button, because both requests carry the same key. If you send the same key with different parameters, such as a different amount, Stripe returns an error and does not charge.

Two other points apply. Stripe's official libraries can retry for you and attach a key automatically, for example the `maxNetworkRetries` option in stripe-node, so check whether your code also has its own retry loop on top of that. Also, retry only on network errors, timeouts, and 5xx responses. Do not retry a 4xx response such as a card decline, because the same request will fail again.

If you want, point me at the checkout file and I will check whether it sends a key and where the retry loop reuses it.
