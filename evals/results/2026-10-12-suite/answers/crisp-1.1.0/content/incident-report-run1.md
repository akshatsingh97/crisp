# Incident report: Checkout API 500 errors

## Summary
On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. A rollback restored service.

## Impact
- Duration: 09:12 to 09:47 UTC (35 minutes).
- Error rate: 18% of checkout API requests returned HTTP 500.
- Number of failed orders and revenue loss: not yet measured. Add these figures.

## Timeline (UTC)
- 09:12: Errors begin. Assumption: the config deploy took effect at this time.
- 09:45: The team rolls back the config change.
- 09:47: Error rate returns to normal. The incident ends.

Add the detection time and the first alert. They were not provided.

## Root cause
A config deploy changed the database pool size from 50 to 5. A pool is a set of reusable database connections. With only 5 connections, requests waited for a free connection. Some of these requests failed with HTTP 500.

Confirm the exact failure mode (for example, connection timeouts) from the logs.

## Resolution
The team rolled back the config deploy at 09:45. The pool size returned to 50. Errors stopped by 09:47.

## What went well
- The rollback fixed the problem.

## What went poorly
- The incident lasted 33 minutes before the rollback began. Add the cause of this delay if known.
- The config change reached production without a check on the pool size value.

## Action items
Owners and dates are blank. Assign them before you publish.

1. Add validation that rejects pool size values below a set minimum.
2. Roll out config changes to a small share of traffic first.
3. Add an alert on database pool exhaustion.
4. Alert on a checkout API 5xx rate above a set threshold.
5. Review why detection and rollback took 33 minutes.
