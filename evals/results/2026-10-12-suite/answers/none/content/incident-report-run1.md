# Incident report: Checkout API errors

**Summary:** On 2026-10-03, the checkout API returned HTTP 500 for 18% of requests for 35 minutes. A config deploy cut the database pool size from 50 to 5. A rollback fixed it.

## Impact

- **Window:** 09:12 to 09:47 UTC (35 minutes).
- **Effect:** 18% of checkout API requests returned HTTP 500.
- **Customer and revenue impact:** Not yet measured. Add the count of failed checkouts and the lost order value.

## Timeline (UTC)

| Time | Event |
|---|---|
| 09:12 | The config deploy changes the database pool size from 50 to 5. Errors start. |
| 09:12 to 09:45 | The checkout API returns HTTP 500 for 18% of requests. |
| 09:45 | The team rolls back the config change. |
| 09:47 | Error rates return to normal. |

Add the time of the first alert and the time someone started to investigate.

## Root cause

The deploy lowered the database pool size to 5. The checkout API needs more connections than that at normal load. Requests that could not get a connection failed with HTTP 500.

The stated facts do not say why the value changed. Possible reasons are a typo, a wrong environment value, or a test value that reached production. Confirm which one applies.

## Resolution

The team rolled back the config at 09:45. The pool size returned to 50. Errors stopped by 09:47.

## What went well

- The rollback restored service within two minutes.

## What went poorly

- The bad value reached production, and nothing stopped it.
- The incident lasted 33 minutes before the rollback started. Add the detection time if you know it.

## Action items

Each item needs an owner and a due date.

1. Add validation that rejects a pool size below a safe minimum.
2. Release config changes to a small share of traffic first, and watch the 5xx rate before a full rollout.
3. Add an alert on database pool exhaustion.
4. Add an alert on the checkout 5xx rate that fires within 5 minutes.
5. Require review for config changes to database settings.

## Open questions

- Why did the value change from 50 to 5?
- Why did only 18% of requests fail, not all of them? Likely reasons are that some requests got a connection and others did not, or that only some instances got the change. Check this.
- How long did it take to detect the problem?
