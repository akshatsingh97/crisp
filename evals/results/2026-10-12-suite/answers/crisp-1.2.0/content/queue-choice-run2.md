Use Postgres if you already run it and expect fewer than a few hundred jobs per second. Use Redis if you need high throughput or you already run Redis.

**Why Postgres fits a small app**
- It adds no new infrastructure to run, monitor, or back up.
- You can enqueue a job in the same transaction as your data change. This avoids lost or phantom jobs.
- It handles thousands of jobs per second with `SELECT ... FOR UPDATE SKIP LOCKED`. This clause lets many workers claim different rows without blocking each other.
- Use a library instead of writing your own. `pg-boss` and `graphile-worker` both support retries, scheduling, and delayed jobs.

**Why Redis fits other cases**
- It is faster and has lower latency for very high job volume.
- `BullMQ` is mature. It supports delayed jobs, repeatable jobs, rate limiting, priorities, and a dashboard.
- Jobs do not add load to your main database.

**Risks with Postgres**
- Heavy queue churn creates dead rows (table bloat). Keep autovacuum healthy and delete old completed jobs.
- Long-running workers hold connections. Size your connection pool for them.
- Heavy job traffic can slow your main queries if both share one database.

**Risks with Redis**
- A crash can lose recent jobs unless you enable AOF persistence (an append-only log on disk).
- Set `maxmemory-policy noeviction`. Any other policy can silently delete queued jobs.
- You cannot enqueue in the same transaction as a Postgres write. If the write succeeds and the enqueue fails, the job is lost.

**Decision rule**
1. If you have Postgres only, start with `pg-boss` or `graphile-worker`.
2. If you already have Redis, or need more than about 1,000 jobs per second, use `BullMQ`.
3. If you outgrow Postgres later, you can move to Redis. Keep your job handlers independent of the queue library to make that easy.
