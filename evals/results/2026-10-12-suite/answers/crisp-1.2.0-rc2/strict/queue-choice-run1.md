Use Postgres if your app already has it and you expect fewer than about 1,000 jobs per second. Use Redis if you need higher speed or already run it.

Why Postgres fits a small app:
- It adds no new service to run, back up, or monitor.
- You can add a job in the same transaction as your data. A failed request then cannot leave a lost or orphan job.
- `SELECT ... FOR UPDATE SKIP LOCKED` lets many workers take jobs without block. It needs Postgres 9.5 or later.
- Jobs are durable. You can query them with SQL.

Why Redis fits other cases:
- It has lower latency and higher throughput.
- BullMQ is a mature Node library. It gives retries, delayed jobs, rate limits, and a dashboard.

Libraries:
- Postgres: pg-boss or Graphile Worker.
- Redis: BullMQ.

Risks:
- Postgres: a queue table with many inserts and deletes can bloat. Tune autovacuum for that table.
- Postgres: a long transaction in a worker can hold a job lock. Keep job transactions short.
- Redis: data lives in memory. If you do not enable AOF (append-only file) persistence, a restart can lose jobs.
- Redis: set `maxmemory-policy noeviction`. Other policies can delete queued jobs when memory is full.
- Redis: you cannot add a job and your data in one transaction. You must handle duplicate and lost jobs in code.

If you run on AWS and want no queue server to manage, SQS is a third option.
