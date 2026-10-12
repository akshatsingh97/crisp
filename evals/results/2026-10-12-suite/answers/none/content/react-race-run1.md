This is a race condition. A slow earlier request can finish after a newer one and overwrite its result.

Say you switch from user A to user B. The effect for A started a fetch, and the effect for B started another. If A's response arrives last, `setData` runs with A's data while the UI shows B.

Fix it by ignoring the result of any effect that is no longer current. Use a cleanup flag, or better, an `AbortController`:

```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setData)
    .catch(err => {
      if (err.name !== 'AbortError') setError(err);
    });

  return () => controller.abort();
}, [userId]);
```

React runs the cleanup before the next effect, so the old request is cancelled when `userId` changes. If your fetch library cannot abort, use a flag instead:

```jsx
useEffect(() => {
  let ignore = false;
  fetchUser(userId).then(data => {
    if (!ignore) setData(data);
  });
  return () => { ignore = true; };
}, [userId]);
```

Two more things to check:
- **Stale data while loading.** Between the switch and the new response, the old user's data stays on screen. Clear it or set a loading state at the start of the effect, or give the component `key={userId}` so React resets it.
- **Missing dependency.** If `userId` is not in the dependency array, the effect does not re-run and you see the old user's data permanently.

To avoid writing this yourself, use TanStack Query or SWR. They handle cancellation, caching, and ordering.
