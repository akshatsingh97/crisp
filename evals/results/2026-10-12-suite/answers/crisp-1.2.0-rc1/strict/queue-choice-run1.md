Use Postgres if your app already has it and you expect fewer than a few hundred jobs per second. Use Redis if you need higher throughput or you already run it.

Why Postgres fits a small app:
- It adds no new service to run, back up, or monitor.
- You can add a job in the same transaction as your data change. This prevents a job without its data, or data without its job.
- The command `SELECT ... FOR UPDATE SKIP LOCKED` lets many workers take jobs without conflict.
- Jobs are durable and easy to inspect with plain SQL.

Libraries for Postgres:
- pg-boss has retries, scheduled jobs, and cron.
- graphile-worker is fast and has a simple API.

Why Redis fits other cases:
- It handles very high job rates with low delay.
- BullMQ gives delayed jobs, rate limits, priorities, and job flows.
- It is a good choice if you already use Redis for cache or sessions.

Risks with Redis:
- It is one more service to run.
- Set `maxmemory-policy noeviction`. Other policies can delete queued jobs when memory is full.
- Enable AOF (append-only file) persistence. Without it, a restart can lose jobs.
- You cannot add a job and a database change in one transaction. Plan for duplicate or missing jobs.

Risks with Postgres:
- Heavy polling and many dead rows can add load. Use LISTEN/NOTIFY, as pg-boss and graphile-worker do, and keep the job table small.
- Long job transactions can block vacuum. Do not hold a transaction open while a job runs.

Make jobs idempotent with either choice. Both systems can run a job more than once after a crash.

If you are unsure, start with Postgres. You can move to Redis later, because both libraries keep the job logic in your handler functions.
