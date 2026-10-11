Your component has a race condition (two operations that finish in an unpredictable order). When you switch from user A to user B, the request for A is still running. If it finishes after the request for B, it calls the state setter last, and the screen shows A's data under B's name.

React does not cancel the old request when the effect runs again. Each effect run starts its own fetch, and each fetch calls `setState` whenever it finishes. Network time varies, so the last response to arrive wins, not the last request you sent.

The fix is to use the cleanup function of the effect. React calls it before the next run of the effect, so you can mark the old request as stale. This example uses an `ignore` flag and an `AbortController`:

```jsx
useEffect(() => {
  const controller = new AbortController();
  let ignore = false;

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then((res) => res.json())
    .then((data) => {
      if (!ignore) setUser(data);
    })
    .catch((err) => {
      if (err.name !== "AbortError") setError(err);
    });

  return () => {
    ignore = true;
    controller.abort();
  };
}, [userId]);
```

The `ignore` flag makes sure that a late response never reaches the state. The `AbortController` also stops the network request, which saves bandwidth. If you use only one, the flag is the more important part.

Also make sure that `userId` is in the dependency array. If it is missing, the effect does not run again, and you see stale data for a different reason. Last, consider a data library such as TanStack Query or SWR. These tools handle cancellation, caching, and ordering for you, so you do not write this logic by hand.
