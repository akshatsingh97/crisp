This is a race condition: an older fetch can finish after a newer one and overwrite the state with the previous user's data.

When you switch from user A to user B, both requests run at the same time. If A's response arrives last, `setUser` stores A's data while the UI shows B. React does not cancel the old request. Network time varies, so response order does not match request order.

Fix it with a cleanup function that marks the old effect as stale:

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

React runs the cleanup before the next effect, so the old request's result is dropped.

You can also cancel the request itself with `AbortController`:

```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setUser)
    .catch(err => {
      if (err.name !== "AbortError") console.error(err);
    });

  return () => controller.abort();
}, [userId]);
```

Two more points:

- Make sure `userId` is in the dependency array. If it is missing, the effect does not rerun on a switch.
- Consider resetting `user` to `null` when `userId` changes. This stops the old user's data from showing while the new one loads.

A library such as TanStack Query or SWR handles this race for you.
