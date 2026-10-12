This is a race condition. Responses can arrive out of order, and the last one to arrive wins, not the last one you asked for.

**What happens**
1. You select user A. The effect starts `fetch(A)`.
2. You switch to user B. The effect starts `fetch(B)`.
3. A's request is slow and B's is fast. B's response arrives first and sets state.
4. A's response then arrives and overwrites the state. The UI shows A's data while `userId` is B.

Nothing in the first effect run cancels or ignores its request. The stale `.then` still calls `setState`.

**Fix 1: ignore stale responses with a cleanup flag**

```jsx
useEffect(() => {
  let ignore = false;

  fetch(`/api/users/${userId}`)
    .then(res => res.json())
    .then(data => {
      if (!ignore) setUser(data);
    });

  return () => {
    ignore = true; // runs when userId changes or the component unmounts
  };
}, [userId]);
```

When `userId` changes, React runs the old effect's cleanup first. That sets `ignore = true` for the old request, so its result is dropped.

**Fix 2: abort the request (better)**

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

This also stops the wasted network work. Ignore `AbortError` so it doesn't show up as a real failure.

**Related tips**
- Reset or clear `user` (and set a loading flag) when `userId` changes. Otherwise the old user's data stays visible while the new one loads.
- Always list `userId` in the dependency array. A missing dependency causes a similar bug, where the effect never re-runs.
- For production code, consider TanStack Query or SWR. They handle cancellation, caching, and out-of-order responses for you.

If you share your component, I can point to the exact line where the stale update happens.
