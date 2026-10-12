Your effect has a race condition. An older request can finish after a newer one and overwrite the state with the wrong user's data.

Here is the sequence:

1. You select user A. The effect starts fetch A.
2. You switch to user B. The effect starts fetch B.
3. Fetch B finishes first and sets B's data.
4. Fetch A finishes later and sets A's data. The screen now shows A while the selected user is B.

React does not cancel the first fetch when the effect runs again. Network responses can arrive in any order.

Fix it with a cleanup function that ignores stale results:

```jsx
useEffect(() => {
  let ignore = false;

  fetch(`/api/users/${userId}`)
    .then(res => res.json())
    .then(data => {
      if (!ignore) setUser(data);
    });

  return () => {
    ignore = true;
  };
}, [userId]);
```

React runs the cleanup before the next effect run. The old request then sets `ignore` to true and drops its result.

You can also cancel the request itself with `AbortController`:

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

An aborted fetch rejects with an `AbortError`. You must ignore that error in your `catch`, or it will show as a failure.

Two related problems can also show the wrong user:

- **Stale data during loading:** The old user's data stays on screen until the new fetch finishes. Call `setUser(null)` at the start of the effect, or show a loading state.
- **Missing dependency:** If `userId` is not in the dependency array, the effect does not re-run on a switch. Add it.

If you fetch often, a library such as TanStack Query or SWR handles this for you. It keys the cache by user ID and drops stale responses.
