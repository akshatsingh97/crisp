# Release notes: JavaScript SDK 3.0

Version 3.0 has one breaking change. You must update your `init()` calls before you upgrade.

## Breaking changes

`init()` now requires the `apiKey` option. If you do not pass it, `init()` will fail.

To migrate:

1. Find every call to `init()` in your code.
2. Add your API key to the options object.

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changes

- The default number of retries changed from 3 to 5. Requests will now retry more often before they fail.
- If you need the old behavior, set the retries option to 3 yourself. (Assumption: the option is named `retries`. Check the option name in your SDK docs.)

## New

- A new `on('error')` event is available. Use it to handle errors in one place.

```js
on('error', (err) => {
  console.error(err);
});
```

## Fixes

- Fixed a memory leak in the websocket reconnect. Long-running apps that reconnect often will now use less memory.
