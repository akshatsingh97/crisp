This is a race condition: an earlier request for the previous user can finish after the request for the new user, and it then overwrites the state with stale data.

Here is the sequence:

1. You select user A. The effect starts fetch A.
2. You switch to user B. The effect starts fetch B.
3. Fetch B returns first and sets B's data.
4. Fetch A returns late and sets A's data. The screen now shows A while the selected user is B.

React does not cancel the old fetch. The old `.then` callback still runs and still calls `setState`.

## Fix 1: abort the request in cleanup

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

The cleanup runs before the next effect, so the old request is cancelled when `userId` changes. Ignore `AbortError`, because it is expected.

## Fix 2: ignore stale results

Use this if your fetch library does not support abort.

```jsx
useEffect(() => {
  let ignore = false;

  fetchUser(userId).then(data => {
    if (!ignore) setUser(data);
  });

  return () => { ignore = true; };
}, [userId]);
```

The cleanup sets `ignore` to true for the old effect run. Its callback then skips `setUser`.

## Also check

- Put `userId` in the dependency array. If it is missing, the effect does not re-run on a switch.
- Reset or clear the old data when `userId` changes, or show a loading state. Otherwise the old user's data stays visible until the new fetch finishes. You can also set `key={userId}` on the component to reset all its state.
- Apply the same guard to `setLoading` and `setError`, not only `setUser`.

## Alternative

A data library such as TanStack Query or SWR handles this for you. It keys each request by user ID, so a late response cannot overwrite another user's data. React docs also recommend this over hand-written fetch effects.

If the bug continues after the fix, share the component code. A missing dependency or a shared ref is the next likely cause.
