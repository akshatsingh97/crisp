This is a race condition between overlapping requests. Each time `userId` changes, the effect starts a new fetch, but nothing cancels or ignores the old one. Responses can arrive out of order:

1. You select user A, which starts fetch A.
2. You switch to user B quickly, which starts fetch B.
3. Fetch B returns and calls `setData(B)`.
4. Fetch A, which was slower, returns afterward and calls `setData(A)`.

The UI now shows A's data while B is selected. The network doesn't guarantee that responses arrive in the order the requests were sent. The old effect's closure is still alive and its `setState` still works, so it overwrites the newer result.

## Fix 1: Ignore stale responses with a cleanup flag

```jsx
useEffect(() => {
  let ignore = false;

  async function load() {
    const res = await fetch(`/api/users/${userId}`);
    const json = await res.json();
    if (!ignore) setUser(json);
  }
  load();

  return () => { ignore = true; };  // runs when userId changes or on unmount
}, [userId]);
```

React runs the cleanup from the previous render before running the next effect. This marks the earlier request as stale, so its result is dropped.

## Fix 2: Abort the request (better)

This also cancels the network work:

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

Aborted fetches reject with `AbortError`. Filter that error out so it doesn't show up as a real failure.

## Related details

- **Reset the loading state.** When `userId` changes, call `setLoading(true)` and optionally `setUser(null)`. Otherwise the old user's data stays on screen until the new data arrives, which looks like the same bug.
- **Check the dependency array.** If `userId` is missing from it, the effect won't re-run at all, and you'll see stale data for a different reason.
- **Strict Mode in development.** React mounts, unmounts and remounts effects, so you'll see a double fetch. This is intentional, and it exposes missing cleanup.
- **Consider a data library.** TanStack Query, SWR, or React 19's `use()` with Suspense handle cancellation, caching, and keying by user ID for you. They're usually a better choice than hand-rolled fetch effects.

If you paste your component, I can point to the exact spot and check for other causes, such as state keyed incorrectly or a memoized callback with a stale closure.
