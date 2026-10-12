Use Postgres if your app already has it and you expect fewer than a few hundred jobs per second. Use Redis if you already run it or need high throughput.

**Why Postgres fits a small app**
- It adds no new service to run, monitor, or back up.
- You can enqueue a job in the same transaction as your data change. This avoids lost jobs and jobs for rolled-back work.
- Jobs are durable by default.
- `pg-boss` and Graphile Worker are mature Node.js libraries. They use `FOR UPDATE SKIP LOCKED`, which lets many workers claim jobs without blocking each other.

**Limits of Postgres**
- Throughput tops out around thousands of jobs per second, depending on hardware.
- Heavy job churn creates dead rows. Autovacuum (Postgres cleanup process) must keep up.
- Workers poll or use `LISTEN/NOTIFY`, so latency is slightly higher than Redis.

**Why Redis fits**
- BullMQ is the standard Node.js library. It is fast and has delayed jobs, retries, rate limiting, priorities, and repeatable jobs.
- Bull Board gives you a ready-made dashboard.

**Risks of Redis**
- Enqueue is not part of your database transaction. A crash between the two writes can lose a job or run it for data that was rolled back.
- You must enable AOF persistence (append-only file, logs every write) to survive restarts.
- You must set `maxmemory-policy noeviction`. Any other policy can silently delete queued jobs.
- It is one more service to run.

**How to decide**
1. If you already run Redis, use BullMQ.
2. If you only run Postgres and load is modest, use pg-boss or Graphile Worker.
3. If you need rate limiting, complex scheduling, or very high volume, add Redis.

Both options keep migration cheap. Put the queue behind a small `enqueue(name, payload)` function so you can switch later.
