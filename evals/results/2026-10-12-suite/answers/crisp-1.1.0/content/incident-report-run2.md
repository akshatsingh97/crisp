# Incident report: Checkout API HTTP 500 errors

## Summary

On 2026-10-03 from 09:12 to 09:47 UTC (35 minutes), the checkout API returned HTTP 500 for 18% of requests. A config deploy cut the database pool size from 50 to 5. We rolled back the config at 09:45, and errors ended by 09:47.

## Impact

- Duration: 35 minutes.
- Scope: 18% of checkout API requests failed with HTTP 500.
- Customer effect: Affected customers could not complete checkout on that attempt.
- Not yet measured: Total failed requests and lost revenue. Add them from logs.

## Timeline (UTC, 2026-10-03)

1. 09:12: Impact starts after the config deploy.
2. 09:45: The team rolls back the config. Pool size returns to 50.
3. 09:47: Errors stop and the incident ends.

Add the exact deploy time, the first alert time, and the time of diagnosis. We do not have them yet.

## Root cause

A config deploy changed the database pool size from 50 to 5. The pool is the set of open database connections the API shares.

Assumption: With only 5 connections, requests waited for a free connection and then timed out. This explains why only 18% of requests failed. Confirm this against the logs.

## Resolution

We rolled back the config deploy at 09:45. The pool size returned to 50 and the error rate returned to normal.

## Gaps to close

- The deploy passed review or automated checks with a value 10 times lower than before. Find out why.
- The incident lasted 33 minutes before the rollback. Find out when the first alert fired and why it took this long.

## Action items

Owners and dates are blank. Assign them in the review.

1. Add a validation rule that blocks a pool size below an agreed minimum.
2. Add an alert on database pool exhaustion and on checkout 500 rate.
3. Roll out config changes to a small share of traffic first, with automatic rollback on errors.
4. Add a check to config review that flags large changes to existing values.
