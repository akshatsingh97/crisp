This is a race condition. Each time `userId` changes, the effect starts a new fetch, but the old fetch is still running. Responses can arrive out of order. If user A's slow request finishes after user B's fast one, the late response calls `setState` last and overwrites B's data with A's.

The fix is to ignore stale responses in the effect's cleanup.

**Option 1: an `ignore` flag**
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

**Option 2: `AbortController`**, which also cancels the network request
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

React runs the cleanup before each re-run of the effect. When `userId` changes, the previous request is marked stale or aborted before the new one starts.

Two related things to check:
- **Stale data while loading:** reset or clear `user` when `userId` changes, or show a loading state. Otherwise the old user's data stays on screen until the new fetch finishes.
- **Use a data library if you can:** TanStack Query, SWR, or React's `use` with Suspense handle cancellation, caching, and race conditions for you, so you don't write this by hand.

If you share your component, I can point to the exact spot.
