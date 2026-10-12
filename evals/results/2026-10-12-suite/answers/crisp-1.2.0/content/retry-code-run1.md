This function calls `func` and retries on failure. It waits `base_delay * factor**attempt` seconds between tries, capped at `max_delay`, with random jitter.

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
    factor: float = 2.0,
    jitter: str = "full",
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
    on_retry: Callable[[int, BaseException, float], None] | None = None,
    **kwargs,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except retry_on as exc:
            if attempt == max_attempts:
                raise

            delay = min(max_delay, base_delay * factor ** (attempt - 1))
            if jitter == "full":
                delay = random.uniform(0, delay)
            elif jitter == "equal":
                delay = delay / 2 + random.uniform(0, delay / 2)
            elif jitter != "none":
                raise ValueError("jitter must be 'full', 'equal', or 'none'")

            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
```

Example:

```python
import requests

resp = retry_with_backoff(
    requests.get,
    "https://api.example.com/data",
    timeout=5,
    max_attempts=6,
    retry_on=(requests.ConnectionError, requests.Timeout),
    on_retry=lambda n, e, d: print(f"try {n} failed: {e}. wait {d:.2f}s"),
)
```

## Parameters

- `func`: The callable to run. Pass its own arguments in `*args` and `**kwargs`.
- `max_attempts`: Total number of calls, including the first. The last failure is re-raised.
- `base_delay`: Wait time in seconds before the first retry.
- `max_delay`: Upper limit for any single wait. It stops the delay from growing without bound.
- `factor`: Multiplier for each retry. With `base_delay=0.5` and `factor=2`, the delay caps are 0.5, 1, 2, 4, and so on.
- `jitter`: Randomness added to each wait.
  - `"full"`: Wait a random time between 0 and the computed delay. This spreads out clients best.
  - `"equal"`: Wait half the delay plus a random half. This keeps a minimum wait.
  - `"none"`: Wait the exact delay.
- `retry_on`: Exception types that trigger a retry. Any other exception is raised at once.
- `on_retry`: Optional callback. It receives the attempt number, the exception, and the delay. Use it for logging or metrics.

## Notes

- Jitter prevents the thundering herd problem. Without it, many clients that fail together will retry together.
- Narrow `retry_on` to transient errors such as timeouts. Do not retry errors like bad input or authentication failure. They will never succeed.
- Only retry idempotent operations, meaning repeated calls cause no extra side effects. A retried payment request can charge twice.
- `time.sleep` blocks the thread. For async code, use `asyncio.sleep` and `await` the call in an async version.
