This function retries a call with exponential backoff and "full jitter", which means each wait is a random value between 0 and the current backoff ceiling.

```python
import random
import time


def retry_with_backoff(
    func,
    *args,
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    factor=2.0,
    jitter=True,
    retry_on=(Exception,),
    on_retry=None,
    **kwargs,
):
    """Call func(*args, **kwargs). Retry on failure with exponential backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except retry_on as exc:
            if attempt == max_attempts:
                raise
            ceiling = min(max_delay, base_delay * factor ** (attempt - 1))
            delay = random.uniform(0, ceiling) if jitter else ceiling
            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
```

Example:

```python
import requests

def fetch():
    r = requests.get("https://example.com/api", timeout=5)
    r.raise_for_status()
    return r.json()

data = retry_with_backoff(
    fetch,
    max_attempts=6,
    retry_on=(requests.ConnectionError, requests.Timeout),
    on_retry=lambda n, e, d: print(f"Attempt {n} failed: {e}. Retrying in {d:.2f}s"),
)
```

## Parameters

- `func`: The function to call. Pass its arguments after it, or as keywords.
- `*args`, `**kwargs`: Passed to `func` unchanged. Do not name a `func` argument `max_attempts` or any other parameter below, because the names will clash.
- `max_attempts`: Total number of calls, including the first one. After the last failure, the function re-raises the original exception.
- `base_delay`: The backoff ceiling in seconds before the first retry.
- `factor`: The multiplier for each later retry. With `base_delay=0.5` and `factor=2`, the ceilings are 0.5, 1, 2, 4, and so on.
- `max_delay`: The upper limit on the ceiling. It stops the wait from growing without bound.
- `jitter`: If `True`, the function waits a random time between 0 and the ceiling. Jitter stops many clients from retrying at the same moment, which can overload a recovering service. If `False`, it waits exactly the ceiling.
- `retry_on`: A tuple of exception types that trigger a retry. Any other exception is raised at once. Narrow this to transient errors such as timeouts. Do not retry on bugs or bad input.
- `on_retry`: An optional callback with the arguments `(attempt, exception, delay)`. Use it for logging or metrics.

## Notes

- The function sleeps and blocks the thread. For `asyncio` code, write an async version that uses `await asyncio.sleep(delay)`.
- Only retry operations that are safe to repeat (idempotent). A retried payment request can charge twice.
- If the server sends a `Retry-After` header, use that value instead of your own delay.
