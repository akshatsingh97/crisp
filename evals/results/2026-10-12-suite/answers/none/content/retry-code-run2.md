Here is a retry function with exponential backoff and full jitter.

```python
import random
import time
from functools import wraps


def retry(
    func,
    *args,
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    multiplier=2.0,
    jitter="full",
    exceptions=(Exception,),
    on_retry=None,
    **kwargs,
):
    """Call func(*args, **kwargs). Retry on failure with exponential backoff."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as exc:
            if attempt == max_attempts:
                raise

            delay = min(max_delay, base_delay * multiplier ** (attempt - 1))
            if jitter == "full":
                delay = random.uniform(0, delay)
            elif jitter == "equal":
                delay = delay / 2 + random.uniform(0, delay / 2)

            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)


def retrying(**options):
    """Decorator form: @retrying(max_attempts=3, exceptions=(IOError,))"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return retry(func, *args, **options, **kwargs)
        return wrapper
    return decorator
```

Example:

```python
import requests

@retrying(max_attempts=4, exceptions=(requests.ConnectionError, requests.Timeout))
def fetch(url):
    return requests.get(url, timeout=5).json()
```

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `max_attempts` | 5 | Total calls, including the first one. After the last failure, the function raises the original error. |
| `base_delay` | 0.5 | Wait time in seconds before the first retry. |
| `max_delay` | 30.0 | Upper limit for any wait. Without it, the delay grows without bound. |
| `multiplier` | 2.0 | Growth factor. With 0.5 and 2.0, the waits are 0.5, 1, 2, 4 seconds, and so on. |
| `jitter` | `"full"` | Random spread of the wait. `"full"` picks a time from 0 to the computed delay. `"equal"` keeps half the delay and randomizes the other half. Any other value turns jitter off. |
| `exceptions` | `(Exception,)` | Only these error types trigger a retry. Other errors raise at once. |
| `on_retry` | `None` | Optional callback `(attempt, exc, delay)` for logging or metrics. |

## Why jitter matters

Without jitter, many clients that fail at the same moment also retry at the same moment. This creates repeated load spikes on a server that is already struggling. Random delays spread the retries over time. Full jitter usually gives the lowest total load. Equal jitter guarantees a minimum wait.

## Cautions

- Narrow `exceptions` to transient errors, such as timeouts. Retrying a bug or a "400 Bad Request" only wastes time.
- Retry only operations that are safe to repeat. A timeout does not tell you if the first call worked. For payments or writes, use an idempotency key.
- Keep `max_attempts` times `max_delay` within your overall time budget.
