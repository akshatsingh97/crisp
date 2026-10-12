# Incident Report: Checkout API 500 Errors

## Summary
On 2026-10-03, a config deploy cut the database pool size from 50 to 5. The checkout API returned HTTP 500 for 18% of requests for 35 minutes. We rolled back the config and the service recovered.

## Impact
- Duration: 09:12 to 09:47 UTC (35 minutes).
- Scope: 18% of checkout API requests returned HTTP 500.
- Customer and revenue impact: not yet measured. Add failed checkout counts and order value here.

## Timeline (UTC)
- 09:12: Config deploy takes effect. Pool size drops from 50 to 5. Errors begin.
- 09:45: Team rolls back the config change.
- 09:47: Error rate returns to normal.

The detection time, alert source, and responder names are missing. Add them before you publish.

## Root cause
The deploy set the database pool size to 5 instead of 50. A pool is a fixed set of reusable database connections. With only 5 connections, requests waited for a free connection, and some failed with HTTP 500.

This explanation is an inference from the pool change. Confirm it with the error logs. Look for pool exhaustion or connection timeout messages.

## Resolution
The team rolled back the config at 09:45. Pool size returned to 50. Errors stopped by 09:47.

## What went well
- The rollback restored service within about 2 minutes.

## What went wrong
- The bad value reached production without a block or review.
- The incident lasted 33 minutes before the rollback began. The cause of the delay is not stated.

## Action items
These are proposed. Assign an owner and a due date to each.
1. Add validation that rejects a pool size below a set minimum.
2. Roll out config changes to a small share of traffic first, then widen.
3. Alert on pool saturation and on a rising 5xx rate for checkout.
4. Review why detection and rollback took 33 minutes. Shorten the path to rollback.
5. Confirm why the value was set to 5. Check whether it was a typo, a wrong environment value, or a unit error.

If you share the detection time, the responders, and the customer impact, I can fill in the gaps.
