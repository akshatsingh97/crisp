This function retries a call with exponential backoff (waits that double each attempt) and full jitter (a random wait to avoid synchronized retries).

```python
import random
import time
from functools import wraps


def retry(
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    multiplier=2.0,
    jitter=True,
    exceptions=(Exception,),
    on_retry=None,
):
    """Decorator: retry a function with exponential backoff and jitter."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == max_attempts:
                        raise
                    delay = min(max_delay, base_delay * multiplier ** (attempt - 1))
                    if jitter:
                        delay = random.uniform(0, delay)
                    if on_retry:
                        on_retry(attempt, exc, delay)
                    time.sleep(delay)
        return wrapper
    return decorator


# Example
@retry(max_attempts=4, base_delay=1, exceptions=(ConnectionError, TimeoutError))
def fetch():
    ...
```

## Parameters

- `max_attempts`: Total number of calls, including the first. After the last failure, the function re-raises the original exception.
- `base_delay`: Wait time in seconds before the first retry. Later waits grow from this value.
- `max_delay`: Upper limit for any single wait. It stops the delay from growing without bound.
- `multiplier`: Growth factor. With 2.0 and a base of 0.5, the waits are 0.5, 1, 2, 4 seconds.
- `jitter`: If true, the function waits a random time between 0 and the computed delay. This is "full jitter". It spreads out retries from many clients so they do not hit a server at the same moment.
- `exceptions`: Tuple of exception types that trigger a retry. Any other exception is raised at once. Always narrow this to errors that are safe to retry.
- `on_retry`: Optional callback with `(attempt, exception, delay)`. Use it for logging or metrics.

## Risks

- Only retry operations that are idempotent (safe to run more than once). Retrying a payment call can charge twice.
- Do not retry permanent errors such as bad input or HTTP 401. Set `exceptions` to cover only temporary failures.
- This version blocks with `time.sleep`. In async code, use `asyncio.sleep` and an `async def` wrapper.
