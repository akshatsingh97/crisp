This is a race condition: an older fetch can finish after a newer one and overwrite the newer result.

**Why it happens**

1. You switch from user A to user B. Both fetches run at the same time.
2. Network order is not guaranteed. A's response can arrive after B's.
3. A's `.then` still calls `setUser(...)`. State now holds A's data while the UI shows B.

React's cleanup function runs when `userId` changes, but it cannot cancel a fetch by itself. Your code must ignore the stale response.

**Fix 1: ignore flag (works with any async call)**

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

**Fix 2: AbortController (also cancels the request)**

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

An aborted fetch rejects with `AbortError`. Filter it out, or it will show as a real error.

**Other things to check**

- Reset or clear `user` and set loading when `userId` changes. Otherwise the old user stays on screen until the new data arrives.
- In development, React Strict Mode runs effects twice. Without cleanup, this also produces duplicate requests.
- Consider a data library such as TanStack Query or SWR. They handle cancellation, caching, and stale responses for you.
