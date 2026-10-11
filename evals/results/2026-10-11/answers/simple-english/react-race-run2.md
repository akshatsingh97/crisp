Your component has a race condition (two operations finish in an unpredictable order). When you switch users, the effect starts a new fetch, but the old fetch is still running. If the old request for user A finishes after the new request for user B, it calls setState last, and the screen shows A's data while the selected user is B.

React does not cancel the old request for you. The effect cleanup function runs before the next effect, so you can use it to mark the old request as stale. This code ignores any result that arrives after the user changed:

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

You can also cancel the request itself with an AbortController. This saves bandwidth, and it works with fetch:

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

If you also want to avoid a brief flash of the old user's data while the new one loads, set the user to null or show a loading state at the start of the effect. A data library such as TanStack Query or SWR handles all of this for you, including caching and request ordering, so it is worth considering if you have many components that fetch data.
