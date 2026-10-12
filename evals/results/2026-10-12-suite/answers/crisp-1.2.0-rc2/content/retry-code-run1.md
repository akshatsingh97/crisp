Use the function below. It retries a call with exponential backoff (the wait grows each attempt) and full jitter (a random wait that prevents many clients from retrying together).

```python
import random
import time
import functools


def retry(
    func,
    *args,
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    factor=2.0,
    jitter=True,
    exceptions=(Exception,),
    on_retry=None,
    **kwargs,
):
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as exc:
            if attempt == max_attempts:
                raise
            delay = min(max_delay, base_delay * factor ** (attempt - 1))
            if jitter:
                delay = random.uniform(0, delay)
            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)


def retrying(**options):
    """Decorator form: @retrying(max_attempts=3, exceptions=(IOError,))"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry(func, *args, **options, **kwargs)
        return wrapper
    return decorator
```

Example:

```python
import requests

def log(attempt, exc, delay):
    print(f"Attempt {attempt} failed: {exc}. Retrying in {delay:.2f}s")

data = retry(
    requests.get, "https://example.com/api",
    max_attempts=4,
    exceptions=(requests.ConnectionError, requests.Timeout),
    on_retry=log,
)
```

## Parameters

- `func`: The function to call. Pass its arguments after it.
- `max_attempts`: Total number of tries, including the first. After the last failure, the function raises the original exception.
- `base_delay`: Wait in seconds after the first failure. With the defaults, the waits grow as 0.5, 1, 2, 4 seconds.
- `max_delay`: Upper limit for any single wait. This stops the delay from growing without bound.
- `factor`: Multiplier for each new wait. A value of 2 doubles the delay every attempt.
- `jitter`: If `True`, the function waits a random time between 0 and the computed delay. This is "full jitter". It spreads out retries from many clients so they do not hit a recovering server at the same moment. Set it to `False` for fixed, predictable waits, for example in tests.
- `exceptions`: Tuple of exception types that trigger a retry. Any other exception is raised at once.
- `on_retry`: Optional callback that receives the attempt number, the exception, and the upcoming delay. Use it for logging or metrics.

## Notes

- Always narrow `exceptions`. The default `Exception` will also retry bugs such as `TypeError`, which will never succeed.
- Only retry idempotent operations (safe to repeat with the same result). A retried payment request can charge twice.
- The function blocks with `time.sleep`. For async code, use `await asyncio.sleep(delay)` in an `async` version.
- Worst-case total wait with the defaults is about 7.5 seconds for 5 attempts, or less with jitter.
