This is a race condition. Each time `userId` changes, the effect fires a new fetch, but nothing cancels the old one. Responses can arrive out of order:

1. You select user A, which starts fetch A.
2. You quickly switch to user B, which starts fetch B.
3. Fetch B resolves, and the component shows B's data.
4. Fetch A resolves late, and its `setState` call overwrites the screen with A's data.

The UI now shows A's data even though B is selected. Network latency isn't ordered, so a slow request that started earlier can finish later.

## Fix 1: Ignore stale responses with a cleanup flag

```jsx
useEffect(() => {
  let ignore = false;

  async function load() {
    const res = await fetch(`/api/users/${userId}`);
    const data = await res.json();
    if (!ignore) setUser(data);
  }
  load();

  return () => { ignore = true; };
}, [userId]);
```

When `userId` changes, React runs the previous effect's cleanup. That sets `ignore = true` for the old request, so its result is discarded.

## Fix 2: Abort the request with AbortController

This is better because it also cancels the network request.

```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setUser)
    .catch(err => {
      if (err.name !== 'AbortError') setError(err);
    });

  return () => controller.abort();
}, [userId]);
```

An aborted fetch rejects with an `AbortError`. Filter it out so it isn't treated as a real failure.

## Related details

- **Reset state when the user changes.** Otherwise the old user's data stays visible while the new one loads. You can call `setUser(null)` at the start of the effect. Alternatively, put `key={userId}` on the component so React remounts it with fresh state.
- **Loading and error state.** Guard these with the same `ignore` flag, or an old request's `finally` can flip `loading` to false too early.
- **Consider a data-fetching library.** TanStack Query, SWR, or RTK Query key their cache by `userId`, so this class of bug goes away.

If you paste your component, I can point to the exact spot to fix.
