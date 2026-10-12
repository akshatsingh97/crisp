# Release Notes: v3.0

Version 3.0 has one breaking change. Read the Breaking changes section before you upgrade.

## Breaking changes

`init()` now requires the `apiKey` option. If you call `init()` without `apiKey`, the call will fail.

To migrate, add `apiKey` to every `init()` call:

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changed

The default number of retries is now 5. The previous default was 3.

If you need the old behavior, set the retry count to 3 in your options. The option name is not part of these notes, so check the SDK reference for it.

## Added

A new `on('error')` event is available. Use it to handle errors that the SDK raises.

```js
on('error', (err) => {
  // handle the error
});
```

The handler signature above is an assumption. Check the SDK reference for the exact event payload.

## Fixed

A memory leak in the websocket reconnect is fixed. Long-running apps that reconnect often will now keep a stable memory use.
