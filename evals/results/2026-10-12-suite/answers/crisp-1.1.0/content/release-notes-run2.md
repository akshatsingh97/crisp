# Release notes: JavaScript SDK 3.0

Version 3.0 has one breaking change. You must pass an `apiKey` option to `init()`.

## Breaking changes

`init()` now requires the `apiKey` option. If you do not pass it, `init()` will fail.

To upgrade:

1. Find every call to `init()` in your code.
2. Add the `apiKey` option to each call.

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changes

- The default number of retries changed from 3 to 5. If you want the old behavior, set the retry count to 3 yourself.
- A new `on('error')` event is available. Use it to handle errors in one place.

## Fixes

- Fixed a memory leak in the websocket reconnect.

I assumed the retry count is a configurable option. The notes do not give its name, so add it if you want that line to be exact.
