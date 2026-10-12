# Incident report: Checkout API HTTP 500 errors

## Summary
On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. A rollback at 09:45 fixed the problem.

## Impact
- Duration: 09:12 to 09:47 UTC (35 minutes).
- Scope: 18% of checkout API requests failed with HTTP 500.
- Customer and revenue impact: not provided. Add the failed order count and estimated lost revenue here.

## Timeline (UTC, 2026-10-03)
- 09:12: Impact starts. The checkout API begins to return HTTP 500.
- 09:45: The team rolls back the config deploy.
- 09:47: Error rate returns to normal. Impact ends.

The deploy time and detection time were not provided. Add both. Check whether the deploy went out before 09:12.

## Root cause
A config deploy changed the database pool size from 50 to 5. The pool was then too small for checkout traffic.

Assumption: requests failed because they could not get a database connection. Confirm this with the error logs and pool metrics.

## Resolution
The team rolled back the config deploy at 09:45. The pool size returned to 50. Errors stopped by 09:47.

## What went well
- The rollback restored service within two minutes.

## What went wrong
- The config change reached production with a pool size 10 times too small.
- Detection took an unknown time. The impact lasted 33 minutes before the rollback began.
- Only 18% of requests failed. This partial failure may have hidden the problem from some alerts.

## Action items
Owners and due dates are not assigned. Add them before you publish.

1. Add validation that blocks pool size values below a set minimum.
2. Roll out config changes to a small share of traffic first, with automatic rollback on errors.
3. Add an alert on checkout API 5xx rate and on database pool saturation.
4. Add a review step for config changes to critical settings.
5. Document the rollback steps so on-call staff can act faster.

If you share the deploy time, detection method, and customer impact, I will complete the missing fields.
