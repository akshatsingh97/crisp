Your effect has a race condition: an older request for the previous user can finish after the newer one and overwrite the state.

Network responses do not arrive in request order. Example: you select user 1, then user 2. Request 2 finishes first and shows user 2. Request 1 finishes later and calls `setUser` with user 1's data. The screen now shows the wrong user.

Fix it with a cleanup function. React runs the cleanup before the next effect, so it can mark the old request as stale.

```jsx
useEffect(() => {
  const controller = new AbortController();

  async function load() {
    try {
      const res = await fetch(`/api/users/${userId}`, { signal: controller.signal });
      const data = await res.json();
      setUser(data);
    } catch (err) {
      if (err.name !== 'AbortError') setError(err);
    }
  }

  load();
  return () => controller.abort();
}, [userId]);
```

`controller.abort()` cancels the old request, so its `setUser` call never runs. The `AbortError` is expected, so ignore it.

If your fetch library cannot abort, use an ignore flag instead:

```jsx
useEffect(() => {
  let ignore = false;
  fetchUser(userId).then(data => {
    if (!ignore) setUser(data);
  });
  return () => { ignore = true; };
}, [userId]);
```

Check these related causes too:

1. Put `userId` in the dependency array. If it is missing, the effect does not rerun on a switch, and the data stays stale.
2. Clear old data when `userId` changes, for example `setUser(null)` at the start of the effect. Otherwise the previous user's data stays visible during loading.
3. Do not read `userId` from an old closure inside async code. Use the value from the effect scope.

For a longer-term fix, use a data library such as TanStack Query or SWR. They key the cache by user ID and handle stale responses for you.
