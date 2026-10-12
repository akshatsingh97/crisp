Your effect has a race condition: an older request can finish after a newer one and overwrite the state with the wrong user's data.

Network responses do not arrive in the order you sent them. Suppose you switch from user A to user B. If A's request is slower, this happens:

1. The effect runs for A and starts fetch A.
2. You switch to B. The effect runs again and starts fetch B.
3. Fetch B finishes and calls `setData(B)`.
4. Fetch A finishes late and calls `setData(A)`. The screen now shows A while the selected user is B.

React does not cancel the old fetch. The old callback still holds its own `setData` and will run when the response arrives.

**Fix 1: ignore stale responses with a cleanup function**

React runs the cleanup before the next effect run. Use it to mark the old request as outdated.

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

**Fix 2: abort the request**

This also saves bandwidth. An aborted `fetch` rejects with an `AbortError`, so you must ignore that error.

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

**Related problems to check**

- Old data stays on screen while the new request loads. Clear it at the start of the effect with `setUser(null)`. You can also give the component `key={userId}` so React resets all its state on each switch.
- If you fetch in an `async` function inside the effect, put the `ignore` check after every `await`, not only the last one.
- Loading and error state have the same race. Guard those setters with the same flag.

**Alternative**

A data library such as TanStack Query or SWR handles this for you. It keys each result by `userId`, so a late response can never replace the current user's data.

If the bug continues after the fix, check that `userId` is in the dependency array. A missing dependency means the effect does not rerun when you switch users.
