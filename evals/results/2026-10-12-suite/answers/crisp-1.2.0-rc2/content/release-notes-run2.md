# Version 3.0 release notes

## Breaking change

`init()` now requires the `apiKey` option. Add `apiKey` to every `init()` call before you upgrade.

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changed

The default number of retries is now 5. The old default was 3. If your code depends on 3 retries, set the retry count explicitly in your configuration.

## Added

A new `on('error')` event is available. Use it to handle SDK errors in one place.

```js
on('error', (error) => {
  console.error(error);
});
```

Assumption: the handler receives the error as its first argument. Check this against the API reference.

## Fixed

A memory leak in the websocket reconnect is fixed. Long-running apps that reconnect often will now keep memory use stable.
