# JavaScript SDK 3.0 release notes

Version 3.0 has one breaking change. `init()` now requires an `apiKey` option. Update your `init()` calls before you upgrade.

## Breaking changes

- `init()` now requires the `apiKey` option. If you leave it out, `init()` fails.

Before:

```js
init({ /* your options */ });
```

After:

```js
init({ apiKey: "YOUR_API_KEY", /* your options */ });
```

## Changed behavior

- The default number of retries is now 5. It was 3. Failed requests now retry more times before they fail, so some calls take longer to report an error. To keep the old behavior, set your retry count to 3 in your configuration.

## New

- You can now listen for errors with `on('error')`. Add a handler to react to SDK errors in one place.

```js
sdk.on('error', (err) => {
  console.error('SDK error:', err);
});
```

## Fixed

- Fixed a memory leak in the websocket reconnect. Long-running apps that reconnect often will now keep a steady memory use.

## Upgrade steps

1. Add `apiKey` to every `init()` call.
2. Check if the new default of 5 retries is right for your app. If not, set the value yourself.
3. Optional: add an `on('error')` handler.

I did not know the exact option name for the retry count or the name of your SDK object (`sdk` above). Replace both with the real names before you publish.
