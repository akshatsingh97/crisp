# Incident Report: Checkout API HTTP 500 Errors

## Summary
On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. Rollback restored service.

## Impact
- Window: 09:12 to 09:47 UTC (35 minutes).
- Scope: 18% of checkout API requests failed with HTTP 500.
- Customer and revenue impact: not yet measured. Add failed order counts here.

## Timeline (UTC)
- 09:12: Config deploy changes the database pool size from 50 to 5. Errors begin.
- 09:45: Team rolls back the config change.
- 09:47: Error rate returns to normal. The incident ends.

The detection time, alert source, and responder names are missing. Add them before you publish.

## Root cause
The deploy set the database pool size to 5 instead of 50. The pool was too small for checkout traffic. Requests that could not get a connection failed with HTTP 500.

This is an inference from the pool size change and the error pattern. Confirm it with connection wait metrics and error logs.

## Resolution
The team rolled back the config deploy at 09:45. The pool size returned to 50.

## What went well
- Rollback fixed the problem.

## What went poorly
- Errors ran for 33 minutes before the rollback.
- The bad value reached production. The review or validation step did not stop it.

## Action items (proposed)
1. Add validation that rejects pool size values far below the current value. Owner: TBD.
2. Add an alert on database connection pool exhaustion and on checkout 5xx rate. Owner: TBD.
3. Roll out config changes to a small share of traffic first, with automatic rollback on error rate. Owner: TBD.
4. Review why the change passed review. Check for a possible typo, such as 5 for 50. Owner: TBD.

I can publish this as a shareable page or adjust the format for your template. Send me the missing details and I will fill them in.
