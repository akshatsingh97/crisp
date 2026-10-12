This is a race condition. Each user switch starts a new fetch, and nothing cancels the old one. Responses can arrive out of order. If user A's slow request finishes after user B's fast one, the effect still calls `setData` with A's data, and A's data overwrites B's.

The effect's cleanup function runs before the next effect, so you can use it to ignore stale responses.

**Option 1: ignore flag**
```jsx
useEffect(() => {
  let ignore = false;

  fetchUser(userId).then(data => {
    if (!ignore) setUser(data);
  });

  return () => { ignore = true; };
}, [userId]);
```

**Option 2: AbortController (also cancels the request)**
```jsx
useEffect(() => {
  const controller = new AbortController();

  fetch(`/api/users/${userId}`, { signal: controller.signal })
    .then(r => r.json())
    .then(setUser)
    .catch(err => {
      if (err.name !== 'AbortError') setError(err);
    });

  return () => controller.abort();
}, [userId]);
```

**Related fixes**
- **Reset state when `userId` changes.** Otherwise the old user's data stays on screen while the new fetch is in flight. You can also set `key={userId}` on the component so React remounts it with fresh state.
- **Make sure `userId` is in the dependency array.** A missing dependency gives a similar symptom.
- **Consider a data library.** TanStack Query or SWR handle cancellation, caching, and keying by user ID for you.

If you share the component, I can check whether something else is also contributing.
