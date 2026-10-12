# Incident Report: Checkout API 500 Errors

## Summary
On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. A rollback at 09:45 restored service.

## Impact
- Start: 09:12 UTC
- End: 09:47 UTC
- Duration: 35 minutes
- Scope: 18% of checkout API requests returned HTTP 500.
- Not yet known: the number of failed orders and the revenue lost. Add these figures from request logs.

## Timeline (UTC, 2026-10-03)
- 09:12: Checkout API begins to return HTTP 500.
- 09:45: Team rolls back the config deploy.
- 09:47: Error rate returns to normal.

The deploy time, the alert time, and the detection time are not in the source facts. Add them.

## Root cause
A config deploy changed the database pool size from 50 to 5. A pool is a set of reusable database connections. With only 5 connections, requests waited for a free connection. Some of those requests failed with HTTP 500.

This explains why only 18% of requests failed instead of all of them. The exact failure mode, such as pool timeout, is an assumption. Confirm it in the application logs.

## Resolution
The team rolled back the config deploy at 09:45. The pool size returned to 50. Errors stopped by 09:47.

## What went well
- The rollback restored service within 2 minutes.

## What went wrong
- A value 10 times lower than the previous one passed review and deploy.
- The change took 33 minutes to reach rollback after errors began, based on the times above.

## Action items
These are proposals. Assign an owner and a due date to each.

1. Add validation to the config pipeline that blocks large drops in the pool size.
2. Roll out config changes to a small share of traffic first, then widen.
3. Add an alert on database pool saturation and on the checkout 5xx rate.
4. Add a rollback runbook step for config deploys.
5. Find out why the change took 33 minutes to detect and roll back. Fix the gap.

## Open questions
- Was the change intentional or a typo?
- Which review step missed it?
- How many orders failed?
