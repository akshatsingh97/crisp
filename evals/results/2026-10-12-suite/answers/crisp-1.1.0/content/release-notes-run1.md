# SDK 3.0 release notes

Version 3.0 has one breaking change. You must pass an `apiKey` option to `init()`.

## Breaking changes

If you call `init()` without `apiKey`, it will fail after you upgrade. Update every call before you deploy 3.0.

1. Find each call to `init()` in your code.
2. Add the `apiKey` option:

   ```js
   init({ apiKey: 'YOUR_API_KEY' });
   ```

## Changed defaults

The default number of retries changed from 3 to 5. Requests that fail will now retry up to five times.

If you need the old behavior, set the retry option to 3 in your configuration. The option name is not listed in this draft, so check the SDK reference.

## New features

A new `on('error')` event is available. Use it to handle errors in one place.

```js
on('error', (err) => {
  // handle the error
});
```

The exact shape of the error object is not listed in this draft. Confirm it in the SDK reference before you rely on it.

## Fixes

Fixed a memory leak in the websocket reconnect. Memory use will now stay stable during repeated reconnects.

I used `init()` and `on()` as written in your notes. I did not add the module name or the error object details. Add them if your readers need them.
