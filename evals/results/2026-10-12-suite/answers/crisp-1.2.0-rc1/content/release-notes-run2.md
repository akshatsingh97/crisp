# Release notes: JavaScript SDK 3.0

Version 3.0 has one breaking change. You must update your `init()` calls before you upgrade.

## Breaking changes

`init()` now requires the `apiKey` option. If you do not pass it, `init()` will fail.

Before you upgrade, find every `init()` call in your code and add `apiKey`:

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changes

The default number of retries is now 5. The previous default was 3. Your requests will retry more often unless you set the retry count yourself. To keep the old behavior, set the retry count to 3. Check the SDK reference for the option name.

## New

The SDK now emits an `error` event. Use `on('error')` to handle errors in one place:

```js
sdk.on('error', (err) => {
  console.error(err);
});
```

This example assumes the handler receives the error as its first argument. Confirm this against the SDK reference.

## Fixed

A memory leak in the websocket reconnect is fixed. Long-running apps that reconnect often will no longer grow in memory use.
