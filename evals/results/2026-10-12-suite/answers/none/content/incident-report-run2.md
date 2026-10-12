# Incident report: checkout API errors

**Summary:** On 2026-10-03, a config deploy cut the database pool size from 50 to 5. For 35 minutes, 18% of checkout API requests failed with HTTP 500. We rolled back the change and the service recovered.

## Impact

- **Duration:** 35 minutes, 09:12 to 09:47 UTC.
- **Effect:** The checkout API returned HTTP 500 for 18% of requests.
- **Customer impact:** Customers who got a 500 could not complete checkout in that request.
- **Not yet known:** The number of failed orders and the revenue lost.

## Timeline (UTC, 2026-10-03)

| Time | Event |
|---|---|
| 09:12 | Errors start after the config deploy. The deploy set the database pool size to 5 instead of 50. |
| 09:45 | We roll back the config change. |
| 09:47 | Error rate returns to normal. The incident ends. |

The deploy time, the alert time, and the time we first noticed the problem are missing. Add them before you share this report.

## Root cause

The config deploy changed the database pool size from 50 to 5. Checkout traffic needs more than 5 connections at once. Requests that could not get a connection failed with HTTP 500. The 18% error rate fits this cause, but we have not confirmed the exact failure mode. Check the pool-exhaustion and timeout errors in the logs.

## Detection and response

- The first 33 minutes passed before the rollback. Add how we detected the problem, and why the rollback took that long.
- The rollback restored the pool size to 50 and ended the errors within 2 minutes.

## Contributing factors

- The deploy applied a 90% pool reduction with no check on the value.
- We saw no automatic stop when the error rate rose after the deploy. Confirm this point.

## Action items

Owners and due dates are missing. Assign them.

1. Add validation that rejects a pool size below a set minimum in config deploys.
2. Roll out config changes in stages, with an automatic rollback when the error rate rises.
3. Add an alert on database pool saturation and on checkout 5xx rate.
4. Review the 33 minutes between the first error and the rollback, and shorten that time.
5. Count the failed checkouts and decide if customers need follow-up.

I did not invent any detail beyond your facts. Send me the missing times, the owners, and the log findings, and I will complete the report.
