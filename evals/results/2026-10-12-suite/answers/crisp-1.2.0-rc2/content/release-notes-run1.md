# JavaScript SDK 3.0 Release Notes

## Breaking changes

`init()` now requires the `apiKey` option. If you omit it, `init()` will fail.

Before:
```js
init();
```

After:
```js
init({ apiKey: 'YOUR_API_KEY' });
```

To upgrade, add `apiKey` to every `init()` call before you deploy 3.0.

## Changes

- The default number of retries changed from 3 to 5. Failed requests will now retry more times before they fail.
- To keep the old behavior, set the retry count to 3 in your options. The option name `retries` is an assumption. Check the SDK reference.

## New

- Added the `on('error')` event. Use it to handle errors in one place.

```js
client.on('error', (err) => {
  console.error(err);
});
```

The `client` variable and the callback argument are examples. Adapt them to your setup.

## Fixed

- Fixed a memory leak in the websocket reconnect. Long-running apps that reconnect often will now keep stable memory use.
