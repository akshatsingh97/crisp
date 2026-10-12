This is a race condition. Your effect starts a fetch for each user ID, but nothing cancels the old fetch when the ID changes.

**What happens**
1. You select user A. Request A starts.
2. You switch to user B. Request B starts.
3. Request B finishes first. State shows B's data.
4. Request A finishes late. It calls `setState` with A's data.
5. The screen now shows A's data while the selected user is B.

Network responses can arrive in any order. The last response to arrive wins, not the last request you sent.

**Fix 1: cleanup flag**
```jsx
useEffect(() => {
  let ignore = false;

  fetchUser(userId).then(data => {
    if (!ignore) setUser(data);
  });

  return () => { ignore = true; };
}, [userId]);
```
React runs the cleanup before the next effect. That marks the old request as stale, so its result is dropped.

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
Aborting saves bandwidth and stops stale responses. Ignore `AbortError`, since it is expected.

**Also check**
- Reset or clear `user` and `loading` when `userId` changes. Otherwise the old user's data shows while the new one loads.
- Put every value the fetch uses in the dependency array.

**Simpler option:** use TanStack Query or SWR. They key the cache by user ID and handle this race for you.
