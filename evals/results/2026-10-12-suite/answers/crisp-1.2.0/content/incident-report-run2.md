# Incident Report: Checkout API 500 Errors

## Summary

On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. The team rolled back the config at 09:45 UTC, and the errors ended at 09:47 UTC.

## Impact

- Duration: 35 minutes (09:12 to 09:47 UTC).
- Affected requests: 18% of checkout API requests returned HTTP 500.
- Customer impact: Some customers could not complete checkout. Exact failed orders and revenue loss are not yet measured.

## Timeline (UTC, 2026-10-03)

| Time | Event |
|---|---|
| 09:12 | Errors start. The config deploy changed the pool size from 50 to 5. |
| 09:45 | Team rolls back the config deploy. |
| 09:47 | Error rate returns to normal. Incident ends. |

Detection time, alert source, and the exact deploy time are missing. Add them before you finalize this report.

## Root Cause

The config deploy set the database connection pool size to 5 instead of 50. With 5 connections, the API could not serve all concurrent checkout requests. Requests that could not get a connection failed with HTTP 500.

This mechanism is an inference from the pool change. Confirm it with pool exhaustion or timeout errors in the API logs.

## Resolution

The team rolled back the config deploy at 09:45. This restored the pool size to 50. Errors stopped two minutes later.

## What Went Well

- Rollback fixed the problem.

## What Went Wrong

- The change from 50 to 5 passed review and deploy without a block.
- Impact lasted 33 minutes before the rollback began.
- Config deploys apparently had no staged rollout or automatic rollback on error rate.

The last point is an assumption. Verify it.

## Action Items

Owners and due dates are blank. Assign them.

1. Confirm whether the value 5 was a typo or an intended change. Record the answer here.
2. Add validation that rejects pool size values below a set minimum.
3. Roll out config changes in stages, with an automatic halt on a rising 5xx rate.
4. Add an alert on database pool exhaustion and on checkout API 5xx rate.
5. Measure failed orders and lost revenue for the 35-minute window.
6. Review why detection and rollback took 33 minutes. Shorten that time.

I can publish this as a shareable page if you want it.
