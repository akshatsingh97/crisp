This function calls `func` and retries it on failure. The wait between tries grows exponentially and gets random jitter (random variation that stops many clients retrying at the same moment).

```python
import random
import time


def retry_with_backoff(
    func,
    *args,
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    multiplier=2.0,
    jitter="full",
    retry_on=(Exception,),
    on_retry=None,
    sleep=time.sleep,
    **kwargs,
):
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except retry_on as exc:
            if attempt == max_attempts:
                raise

            delay = min(max_delay, base_delay * multiplier ** (attempt - 1))

            if jitter == "full":
                delay = random.uniform(0, delay)
            elif jitter == "equal":
                delay = delay / 2 + random.uniform(0, delay / 2)
            elif jitter != "none":
                raise ValueError(f"unknown jitter mode: {jitter!r}")

            if on_retry:
                on_retry(attempt, exc, delay)
            sleep(delay)
```

Example:

```python
import requests

def fetch():
    r = requests.get("https://api.example.com/data", timeout=5)
    r.raise_for_status()
    return r.json()

data = retry_with_backoff(
    fetch,
    max_attempts=6,
    retry_on=(requests.ConnectionError, requests.Timeout),
    on_retry=lambda n, e, d: print(f"try {n} failed: {e}. Waiting {d:.2f}s"),
)
```

## Parameters

- `func`: The callable to run. Pass its arguments through `*args` and `**kwargs`.
- `max_attempts`: The total number of calls, including the first one. The default is 5. The value must be 1 or more.
- `base_delay`: The wait in seconds before the first retry, before jitter. The default is 0.5.
- `max_delay`: The upper limit for any single wait. It stops the delay from growing without bound. The default is 30 seconds.
- `multiplier`: The growth factor per attempt. The delay is `base_delay * multiplier ** (attempt - 1)`. With the defaults, the waits are 0.5, 1, 2, 4 seconds.
- `jitter`: The randomization mode.
  - `"full"` picks a random wait between 0 and the computed delay. It spreads load best and is the default.
  - `"equal"` keeps half the delay and randomizes the other half. It guarantees a minimum wait.
  - `"none"` uses the exact delay. Avoid it when many clients call the same service.
- `retry_on`: A tuple of exception types that trigger a retry. Other exceptions pass through at once. The default retries any `Exception`.
- `on_retry`: An optional callback called as `on_retry(attempt, exception, delay)` before each wait. Use it for logging or metrics.
- `sleep`: The function that waits. Replace it with a fake in tests so they run instantly.

## Notes

- Narrow `retry_on` in real code. Retrying on errors such as `ValueError` or HTTP 400 only repeats a request that will never succeed.
- If every attempt fails, the function re-raises the last exception with its original traceback.
- Only retry operations that are safe to repeat (idempotent). A repeated payment request can charge twice.
- This version is synchronous. For `asyncio`, use `await asyncio.sleep(delay)` and `await func(...)` instead.
