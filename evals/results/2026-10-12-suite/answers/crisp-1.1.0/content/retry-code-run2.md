The function below retries a call with exponential backoff and full jitter. Full jitter means each wait is a random value between 0 and the current backoff cap.

```python
import random
import time


def retry_with_backoff(
    func,
    *,
    args=(),
    kwargs=None,
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0,
    multiplier=2.0,
    exceptions=(Exception,),
    on_retry=None,
):
    kwargs = kwargs or {}
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as exc:
            if attempt == max_attempts:
                raise
            cap = min(max_delay, base_delay * multiplier ** (attempt - 1))
            delay = random.uniform(0, cap)  # full jitter
            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
```

Example:

```python
import requests

result = retry_with_backoff(
    requests.get,
    args=("https://example.com/api",),
    kwargs={"timeout": 5},
    exceptions=(requests.ConnectionError, requests.Timeout),
    on_retry=lambda n, e, d: print(f"Attempt {n} failed: {e}. Retrying in {d:.2f}s"),
)
```

## Parameters

- `func`: The function to call. Pass its positional arguments in `args` and its keyword arguments in `kwargs`.
- `max_attempts`: The total number of calls, including the first one. The default is 5. After the last failure, the function raises the original exception.
- `base_delay`: The backoff cap before the first retry, in seconds. The default is 1.0.
- `multiplier`: The factor that grows the cap after each failure. With the defaults, the caps are 1, 2, 4, and 8 seconds.
- `max_delay`: The upper limit for the cap, in seconds. It stops the wait from growing without bound.
- `exceptions`: A tuple of exception types that trigger a retry. Any other exception is raised at once. Narrow this to transient errors, such as timeouts.
- `on_retry`: An optional callback. It receives the attempt number, the exception, and the delay. Use it for logging or metrics.

## Why jitter matters

Without jitter, many clients that fail together retry at the same moments. This creates repeated load spikes on the failing service. Random delays spread those retries over time.

## Risks

- Only retry operations that are safe to repeat. A retried payment or write can run twice unless the operation is idempotent (repeating it gives the same result).
- The function blocks the thread while it sleeps. In `asyncio` code, you must use `await asyncio.sleep(delay)` in an async version.
