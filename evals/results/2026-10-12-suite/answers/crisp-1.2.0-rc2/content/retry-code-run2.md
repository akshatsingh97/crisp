The function below retries a call with exponential backoff and full jitter. It sleeps for a random time between 0 and the current backoff limit.

```python
import random
import time
from functools import wraps


def retry_with_backoff(
    func,
    *args,
    max_retries=5,
    base_delay=0.5,
    max_delay=30.0,
    factor=2.0,
    jitter=True,
    exceptions=(Exception,),
    on_retry=None,
    **kwargs,
):
    """Call func(*args, **kwargs) and retry on failure."""
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as exc:
            if attempt == max_retries:
                raise
            delay = min(max_delay, base_delay * factor ** attempt)
            if jitter:
                delay = random.uniform(0, delay)
            if on_retry:
                on_retry(attempt + 1, exc, delay)
            time.sleep(delay)


def retry(**options):
    """Decorator form of retry_with_backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry_with_backoff(func, *args, **options, **kwargs)
        return wrapper
    return decorator
```

Example:

```python
import requests

@retry(max_retries=4, base_delay=1, exceptions=(requests.RequestException,))
def fetch(url):
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()
```

## Parameters

- `func`: the function to call. Pass its arguments after it. They go to `func` unchanged.
- `max_retries`: the number of retries after the first attempt. The default 5 gives 6 calls in total. If all calls fail, the last exception is raised.
- `base_delay`: the backoff limit before the first retry, in seconds.
- `factor`: the multiplier for each retry. The limit is `base_delay * factor ** attempt`. With the defaults, the limits are 0.5, 1, 2, 4, and 8 seconds.
- `max_delay`: the cap on the limit. It stops the wait from growing without bound.
- `jitter`: if `True`, the function sleeps for a random time between 0 and the limit. This is called full jitter. It spreads out clients that fail at the same time, so they do not retry together and overload a recovering service. If `False`, the delay is the exact limit.
- `exceptions`: a tuple of exception types that trigger a retry. Any other exception is raised at once. Keep this list narrow. Do not retry errors that cannot succeed, such as bad input or HTTP 4xx errors.
- `on_retry`: an optional callback. It receives the retry number, the exception, and the delay. Use it for logging or metrics.

## Notes

- The function must be safe to call again. If it is not idempotent (a repeat call has the same effect as one call), a retry can duplicate side effects such as payments.
- If you need a minimum wait, replace `random.uniform(0, delay)` with `delay / 2 + random.uniform(0, delay / 2)`. This is called equal jitter.
- For async code, use `await asyncio.sleep(delay)` and `await func(...)` instead. The logic stays the same.
- The `tenacity` library offers the same behavior with more options, if you prefer a tested package.
