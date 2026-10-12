# Incident Report: Checkout API 500 Errors

## Summary

On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. We rolled back the change and service recovered.

## Impact

- Duration: 35 minutes, from 09:12 to 09:47 UTC.
- Scope: 18% of checkout API requests failed with HTTP 500.
- Customer and revenue impact: not yet measured. Add the count of failed orders here.

## Timeline (UTC, 2026-10-03)

- 09:12: The config deploy took effect. Checkout 500 errors began. (Assumption: the deploy time matches the start of impact.)
- 09:45: The team rolled back the config change.
- 09:47: Error rates returned to normal. Impact ended.

Add the detection time, alert name, and responder actions if you have them.

## Root Cause

A config deploy changed the database pool size from 50 to 5. A pool is the set of open database connections that requests share. With only 5 connections, requests could not get a connection fast enough. A share of them failed with HTTP 500.

## Resolution

The team rolled back the config deploy at 09:45. The pool size returned to 50. Errors stopped by 09:47.

## Gaps To Investigate

- The rollback came 33 minutes after impact began. Find out why detection or response took that long.
- The change passed review or deploy checks with a 10x reduction in pool size. Find out why.
- Only 18% of requests failed, so the pool was undersized but not fully exhausted. Confirm this with pool metrics.

## Action Items

Owners and due dates are blank. Assign them before you publish.

1. Add validation that blocks or flags a large change to the pool size in a config deploy.
2. Roll out config changes in stages, with automatic rollback if the checkout error rate rises.
3. Add an alert on database pool saturation and on the checkout 5xx rate.
4. Review the config change process for database settings.
