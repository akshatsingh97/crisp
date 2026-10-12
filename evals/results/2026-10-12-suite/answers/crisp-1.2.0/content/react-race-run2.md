This is a race condition. An older fetch can finish after a newer one and overwrite the state with the wrong user's data.

Here is the sequence:

1. You select user A. The effect starts fetch A.
2. You switch to user B. The effect starts fetch B.
3. Fetch B finishes first and sets B's data.
4. Fetch A finishes later and sets A's data. The screen now shows A while the selected user is B.

Network responses do not return in request order. React does not cancel the old request when the effect re-runs.

Fix it with a cleanup function. Cleanup runs before the next effect and on unmount. Use it to ignore stale results.

Option 1: an `ignore` flag.

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

Option 2: `AbortController`. This also cancels the network request.

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

Aborted fetches reject with an `AbortError`. Handle it, or you will see unhandled errors in the console.

Two related checks:

- Make sure `userId` is in the dependency array. If it is missing, the effect will not re-run on a switch.
- Clear or reset `user` when `userId` changes. If you do not, the old user's data shows while the new fetch loads. That looks like wrong data too.

Alternative: use a data library such as TanStack Query or SWR. They key the cache by user ID and handle stale responses for you.
