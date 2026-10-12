Use Postgres if your app already has it and you run fewer than about 1,000 jobs per second. Otherwise use Redis. The 1,000 figure is a rough estimate, not a hard limit.

Reasons:
- Postgres adds no new service to run. A job can commit in the same transaction as your data, so no job is lost or run twice by mistake.
- Redis is faster and has mature Node libraries, for example BullMQ. It adds a second service to deploy and monitor.
- Redis can lose jobs in a crash unless you turn on AOF (append-only file) persistence.

If you choose Postgres:
1. Install pg-boss or Graphile Worker. Both handle retries, schedules, and delays.
2. If you write your own queue, have each worker select jobs with `FOR UPDATE SKIP LOCKED`. This lets many workers take different jobs without blocking each other.

If you choose Redis, use BullMQ. Set AOF persistence before you go to production.
