# JavaScript SDK 3.0 release notes

Version 3.0 requires an `apiKey` in `init()`, raises the default retries to 5, adds an error event, and fixes a websocket memory leak.

## Breaking change

`init()` now requires the `apiKey` option. If you do not pass it, `init()` will not work.

Before you upgrade, find every `init()` call in your code. Then add `apiKey` to each one:

```js
init({ apiKey: "YOUR_API_KEY" });
```

## Changed

The default number of retries changed from 3 to 5. Requests that fail will now retry up to two more times. If your code depends on 3 retries, set the retry count yourself.

## Added

The SDK now emits an `error` event. Use `on('error')` to listen for it:

```js
on('error', (err) => {
  // Handle the error here
});
```

Assumption: the handler receives the error as its first argument. Check this against the API reference before you ship.

## Fixed

A memory leak in the websocket reconnect is fixed. Long-running apps that reconnect often will now use stable memory.
