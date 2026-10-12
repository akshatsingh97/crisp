This function retries a call with exponential backoff and "full jitter", which means each wait is a random value between 0 and the current backoff cap.

```python
import random
import time
from typing import Callable, Tuple, Type, TypeVar

T = TypeVar("T")


def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_attempts: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    multiplier: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    on_retry: Callable[[int, BaseException, float], None] | None = None,
    **kwargs,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as exc:
            if attempt == max_attempts:
                raise

            cap = min(max_delay, base_delay * (multiplier ** (attempt - 1)))
            delay = random.uniform(0, cap) if jitter else cap

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
    exceptions=(requests.ConnectionError, requests.Timeout),
    on_retry=lambda n, e, d: print(f"Attempt {n} failed: {e}. Retrying in {d:.2f}s"),
)
```

## Parameters

- `func`: The function to call. Pass it without parentheses.
- `*args`, `**kwargs`: Any extra positional and keyword arguments go to `func` on every attempt. Because of this, `func` cannot use the names of the keyword-only parameters below.
- `max_attempts`: The total number of calls, including the first one. The default is 5. A value of 1 means no retry.
- `base_delay`: The backoff cap in seconds before the first retry. The default is 0.5.
- `max_delay`: The upper limit for any wait. It stops the cap from growing without bound. The default is 30 seconds.
- `multiplier`: The growth factor per attempt. With 2.0 and a base of 0.5, the caps are 0.5, 1, 2, 4, 8 and so on.
- `jitter`: If True, the function waits a random time between 0 and the cap. This stops many clients from retrying at the same moment (a "thundering herd"). If False, the wait equals the cap exactly.
- `exceptions`: A tuple of exception types that trigger a retry. Any other exception is raised at once. Narrow this tuple for real code. The default of `Exception` also retries bugs such as `TypeError`, which will not succeed on retry.
- `on_retry`: An optional callback. It receives the attempt number, the exception, and the delay. Use it for logging or metrics.

## Notes

- After the last attempt fails, the function re-raises the original exception with its traceback.
- Only retry operations that are safe to repeat (idempotent). A retried payment call can charge twice.
- If the server sends a `Retry-After` header, honor it instead of the computed delay.
- To use this as a decorator, wrap it with `functools.wraps` and call `retry_with_backoff(fn, *a, **kw)` inside the wrapper.
