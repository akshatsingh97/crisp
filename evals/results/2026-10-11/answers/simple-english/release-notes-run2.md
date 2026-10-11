Here are the release notes for version 3.0. They list one breaking change first, then the other changes.

```markdown
# JavaScript SDK 3.0

Version 3.0 has one breaking change, one new default, one new event, and one bug fix.

## Breaking change

The `init()` function now requires the `apiKey` option. A call to `init()` without `apiKey` is no longer valid.

To upgrade, add `apiKey` to every call to `init()`:

    init({ apiKey: "YOUR_API_KEY" });

## Changed default

The default number of retries changed from 3 to 5. If you want the old behavior, set the number of retries to 3 in your configuration.

## New feature

The SDK now emits an `error` event. You can listen for it with `on('error', handler)`.

## Fixed

We fixed a memory leak in the websocket reconnect. Memory use no longer grows each time the connection reconnects.
```

I did not know the name of the retries option or the exact failure when `apiKey` is missing, so the notes do not name either. Add them if you want readers to see them. I also assumed the memory leak grew with each reconnect, so correct that last sentence if the cause was different.
