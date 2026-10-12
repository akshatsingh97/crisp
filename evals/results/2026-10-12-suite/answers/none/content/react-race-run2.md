This is a **race condition between overlapping requests**. Nothing cancels or ignores the earlier request when the user changes, so responses can arrive out of order.

1. You select user A, which starts `fetch(A)`.
2. You switch to user B quickly, which starts `fetch(B)`.
3. `fetch(B)` is fast and returns first, so `setData(B)` runs.
4. `fetch(A)` is slow and returns later, so `setData(A)` runs.
5. The UI now shows A's data while the selected user is B.

The effect re-runs when `userId` changes, but the old effect's async callback is still alive. It closes over `setData` and writes to state whenever it resolves, whether or not it's still relevant.

## Fix 1: Abort the request in cleanup (best)

```jsx
useEffect(() => {
  const controller = new AbortController();

  async function load() {
    try {
      const res = await fetch(`/api/users/${userId}`, { signal: controller.signal });
      const json = await res.json();
      setData(json);
    } catch (err) {
      if (err.name !== 'AbortError') setError(err);
    }
  }
  load();

  return () => controller.abort();
}, [userId]);
```

React runs the cleanup before the next effect, so the stale request is cancelled.

## Fix 2: Ignore stale results with a flag

Use this when you can't abort, for example with a non-fetch async API:

```jsx
useEffect(() => {
  let ignore = false;

  fetchUser(userId).then(json => {
    if (!ignore) setData(json);
  });

  return () => { ignore = true; };
}, [userId]);
```

## Related issue: stale data while loading

Even with the race fixed, after switching users the old user's data stays on screen until the new data arrives. Reset or flag loading when `userId` changes:

```jsx
useEffect(() => {
  setData(null);   // or setLoading(true)
  ...
}, [userId]);
```

Alternatively, render with `key={userId}` on the component so React remounts it with fresh state for each user.

## Consider a data library

TanStack Query, SWR, or RTK Query handle cancellation, caching, and keying by user ID for you. They're usually a better choice than hand-rolled fetch effects.

If you paste your component, I can point to the exact spot.
