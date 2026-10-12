# Release notes: JavaScript SDK 3.0

Version 3.0 has one breaking change. `init()` now requires an `apiKey`. Read the migration step before you upgrade.

## Breaking changes

- `init()` now requires the `apiKey` option. If you omit it, `init()` fails.

To migrate, pass your key when you call `init()`:

```js
// Before (2.x)
init();

// After (3.0)
init({ apiKey: 'YOUR_API_KEY' });
```

## Changes in behavior

- The default number of retries is now 5. It was 3. Failed requests now take longer to give up. To keep the old behavior, set the retry option to 3 in your `init()` call.

## New features

- You can now listen for errors with `on('error')`. Use it to log or handle errors in one place.

## Bug fixes

- Fixed a memory leak in the websocket reconnect. Long-running apps that reconnect often will now use less memory over time.

I did not name the retry option, because you did not give me its name. Replace "the retry option" with the real option name before you publish. If you also want an example for `on('error')`, send me the handler signature.
