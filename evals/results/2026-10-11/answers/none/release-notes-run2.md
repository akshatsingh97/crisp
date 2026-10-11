# JavaScript SDK 3.0 Release Notes

## ⚠️ Breaking Changes

**`init()` now requires an `apiKey` option.**
Calls to `init()` without `apiKey` will now fail. Update your initialization code:

```js
// Before (2.x)
sdk.init();

// After (3.0)
sdk.init({ apiKey: 'YOUR_API_KEY' });
```

## Changed

- **Default retries increased from 3 to 5.** Requests now retry up to 5 times by default. To keep the old behavior, set the retry option explicitly to `3`.

## Added

- **New `on('error')` event.** Subscribe to errors emitted by the SDK:

  ```js
  sdk.on('error', (err) => {
    console.error('SDK error:', err);
  });
  ```

## Fixed

- **Memory leak in WebSocket reconnect.** Resolved a leak that occurred during reconnection, improving stability for long-running connections.

## Upgrade Checklist

1. Add `apiKey` to your `init()` call.
2. Review any code that depends on the previous default of 3 retries.
3. (Optional) Add an `on('error')` handler.

Note: I didn't know the exact name of the retry option or the `on()` handler signature, so the snippets use plausible placeholders. Adjust them to match your API.
