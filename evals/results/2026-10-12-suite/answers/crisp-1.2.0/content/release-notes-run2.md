# Release notes: JavaScript SDK 3.0

Version 3.0 has one breaking change. You must pass `apiKey` to `init()`.

## Breaking changes

`init()` now requires the `apiKey` option. If you omit it, `init()` will fail.

To upgrade:

1. Find every call to `init()` in your code.
2. Add the `apiKey` option to each call.

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changes

- The default number of retries changed from 3 to 5. Requests that fail will now retry up to 5 times. To keep the old behavior, set the retry count to 3 in your options.
- A new `on('error')` event is available. Use it to handle SDK errors in one place.

```js
sdk.on('error', (err) => {
  console.error(err);
});
```

## Fixes

- Fixed a memory leak in the websocket reconnect.

## Assumptions

- The retry option name is not in the changes you gave me. Check the real option name before you publish the retry advice.
- The `sdk` variable in the `on('error')` example is a placeholder. Replace it with the real object name.
