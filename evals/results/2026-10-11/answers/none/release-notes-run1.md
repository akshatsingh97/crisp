# Release Notes: v3.0

## ⚠️ Breaking Changes

**`init()` now requires an `apiKey` option.**
Calling `init()` without `apiKey` will now fail. Update all initialization calls:

```js
// Before
init();

// After
init({ apiKey: 'YOUR_API_KEY' });
```

## ✨ New Features

- **`on('error')` event.** You can now listen for errors directly:

  ```js
  client.on('error', (err) => {
    console.error('SDK error:', err);
  });
  ```

## 🔄 Changes

- **Default retries increased from 3 to 5.** If you rely on the previous behavior, set the retry option explicitly to `3`.

## 🐛 Bug Fixes

- Fixed a memory leak in the websocket reconnect logic.

## Upgrade Notes

1. Add `apiKey` to every `init()` call.
2. Review any retry-sensitive behavior (timeouts, rate limits) given the new default of 5.
3. Optionally add an `on('error')` handler.

I made up the code examples, including the `client` variable and the retry option name. Please check them against your actual API.
