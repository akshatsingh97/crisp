This is a race condition: each fetch runs to completion, and a slow response for the old user can arrive after the response for the new user. The late response then overwrites state with the old user's data.

Example: you switch from user A to user B. The request for A is slow, and the request for B is fast. B's data sets state first, then A's response arrives and replaces it. The effect cleanup does not cancel the old request unless you write that code.

Fix it with a cleanup function that ignores stale results:

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

React runs the cleanup before the next effect, so the old request sets `ignore = true` when `userId` changes. Its response is then discarded.

You can also cancel the request itself with `AbortController`:

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

Abort throws an `AbortError`, so you must filter it out in `catch`. Otherwise it will show as a failed request.

Also check these two points:
- Include `userId` in the dependency array. If you leave it out, the effect does not rerun on a switch.
- Reset or show a loading state when `userId` changes. Otherwise the old user's data stays on screen until the new data arrives.

If you use a data library such as React Query or SWR, it handles this for you.
