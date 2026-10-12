Here is a decorator-free function that retries a call with exponential backoff and "full jitter".

```python
import random
import time


def retry(
    func,
    *args,
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    multiplier=2.0,
    jitter=True,
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
                raise  # out of attempts: pass the last error to the caller

            delay = min(max_delay, base_delay * multiplier ** (attempt - 1))
            if jitter:
                delay = random.uniform(0, delay)  # "full jitter"

            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
```

Example:

```python
import requests

resp = retry(
    requests.get, "https://api.example.com/data",
    timeout=5,
    max_attempts=4,
    exceptions=(requests.ConnectionError, requests.Timeout),
    on_retry=lambda n, e, d: print(f"Attempt {n} failed ({e}); retrying in {d:.2f}s"),
)
```

## Parameters

| Parameter | Meaning |
|---|---|
| `func`, `*args`, `**kwargs` | The function to call and its arguments. |
| `max_attempts` | Total tries, including the first. After the last failure, the error is raised again. |
| `base_delay` | Wait time in seconds before the first retry. |
| `multiplier` | The delay grows by this factor each attempt. With 0.5 and 2.0, the waits are 0.5, 1, 2, 4 seconds. |
| `max_delay` | Upper limit for one wait. It stops the delay from growing without bound. |
| `jitter` | If `True`, the function waits a random time between 0 and the computed delay. |
| `exceptions` | Only these error types cause a retry. Other errors are raised at once. |
| `on_retry` | Optional callback `(attempt, exc, delay)` for logging or metrics. |

## Why jitter matters

Without jitter, many clients that fail together also retry together. This creates repeated load spikes on a service that is already struggling. Random delays spread the retries out over time.

## Cautions

- Set `exceptions` to specific transient errors, such as timeouts. Do not retry errors like `ValueError` or HTTP 400, because a retry cannot fix them.
- Retry only operations that are safe to repeat. A timed-out `POST` may have succeeded, so use an idempotency key or skip the retry.
- For `asyncio` code, use `await asyncio.sleep(delay)` instead of `time.sleep`. Otherwise the event loop blocks.
