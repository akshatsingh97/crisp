# Release notes: version 3.0

Version 3.0 has one breaking change. You must pass an `apiKey` option to `init()`.

## Breaking changes

Before you upgrade, find every `init()` call in your code. Add the `apiKey` option to each call.

```js
init({ apiKey: 'YOUR_API_KEY' });
```

Calls to `init()` without `apiKey` are no longer supported.

## Changed

- The default number of retries is now 5. The previous default was 3.
- Failed requests can now take longer to report an error.
- To keep the old behavior, set the retry count to 3 in your configuration.

## Added

- New `on('error')` event. Add a listener with `on('error', handler)` to handle errors in one place.

## Fixed

- Fixed a memory leak in the websocket reconnect. The leak happened each time the websocket reconnected.

I did not know your retry option name or the `on('error')` handler signature, so the notes do not name them. Add them if you want.
