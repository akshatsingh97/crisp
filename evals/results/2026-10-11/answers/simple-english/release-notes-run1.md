Here are the release notes for version 3.0. They are in a code block so you can copy them.

````markdown
# Version 3.0

Version 3.0 has one breaking change. You must update your init() call before you upgrade.

## Breaking change

The init() function now requires the apiKey option. If you call init() without apiKey, the call fails.

Before:

```js
init();
```

After:

```js
init({ apiKey: 'YOUR_API_KEY' });
```

## Changes

The default number of retries changed from 3 to 5. A retry is a new attempt after a failed request. If you need the old value, set the number of retries to 3 in your configuration.

The SDK has a new error event. To receive errors, add a handler with on('error').

## Fixes

The websocket reconnect code leaked memory. This release fixes the leak.
````

I did not name the option that sets the number of retries because I do not know its name. Replace that sentence with the exact option name from your API.
