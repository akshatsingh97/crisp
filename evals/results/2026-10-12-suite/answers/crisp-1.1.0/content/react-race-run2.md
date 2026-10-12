This is a race condition: an older fetch can finish after a newer one and overwrite the state with the wrong user's data.

When you switch from user A to user B quickly, both requests run at the same time. Network timing is not ordered. If A's response arrives last, `setData` runs with A's data while the UI shows user B.

Fix it with a cleanup function that ignores stale responses:

```jsx
useEffect(() => {
  let ignore = false;

  fetch(`/api/users/${userId}`)
    .then(res => res.json())
    .then(data => {
      if (!ignore) setData(data);
    });

  return () => {
    ignore = true;
  };
}, [userId]);
```

React runs the cleanup before the next effect, so the old request sets `ignore = true` when `userId` changes. Its result is then dropped.

To also cancel the network request, use `AbortController`:

```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setData)
    .catch(err => {
      if (err.name !== "AbortError") setError(err);
    });

  return () => controller.abort();
}, [userId]);
```

Abort rejects the promise with an `AbortError`. You must filter it out in `catch`, or it will show as an error.

Two related points:

- Also reset `data` and set a loading state when `userId` changes. Otherwise the old user's data stays visible while the new one loads.
- A data library such as TanStack Query or SWR handles this for you, including caching and cancellation.
