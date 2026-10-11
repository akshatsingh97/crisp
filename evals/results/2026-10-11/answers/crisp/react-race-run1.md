This is a race condition: an older request for the previous user can finish after the newer one and overwrite the state with stale data.

When you switch users, each change of `userId` starts a new fetch. Network responses do not arrive in order. If user A's slow request resolves after user B's fast one, `setUser` runs last with A's data. React does not cancel the old effect's async work, so nothing stops it.

Fix it with a cleanup function that marks the old effect as stale:

```jsx
useEffect(() => {
  let ignore = false;

  fetchUser(userId).then(data => {
    if (!ignore) setUser(data);
  });

  return () => {
    ignore = true;
  };
}, [userId]);
```

React runs the cleanup before the next effect, so the old request's result is dropped.

To also cancel the network call, use `AbortController`:

```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setUser)
    .catch(err => {
      if (err.name !== "AbortError") setError(err);
    });

  return () => controller.abort();
}, [userId]);
```

Two related points:

- Reset or show a loading state when `userId` changes. Otherwise the old user's data stays visible until the new data arrives.
- A data library such as TanStack Query or SWR handles this for you, including caching and cancellation.
