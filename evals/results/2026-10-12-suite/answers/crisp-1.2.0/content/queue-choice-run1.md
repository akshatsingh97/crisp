Use Postgres if your app already has it and you expect fewer than about 1,000 jobs per second. Add Redis only when you need more than that or already run it.

**Why Postgres fits a small app**
- It adds no new service to run, monitor, or back up.
- You can enqueue a job in the same transaction as your data change. A job never exists without its row, and a row never lacks its job.
- Jobs survive restarts with normal database durability.
- You can inspect and fix jobs with plain SQL.
- Libraries use `SELECT ... FOR UPDATE SKIP LOCKED`, which lets many workers take different jobs without blocking each other. Good options are `pg-boss` and Graphile Worker.

**Why Redis fits other cases**
- Throughput is higher, and latency is lower.
- BullMQ is a mature library with retries, delays, rate limits, priorities, and repeatable jobs.
- Redis suits large volumes of short jobs.

**Risks**
- Redis can lose jobs on a crash unless you enable AOF (append-only file) persistence. Even then, a small window of loss remains.
- Redis adds a second system to operate. It also cannot join the transaction in your Postgres write.
- Postgres queues create table bloat and write load at high volume. Tune autovacuum and delete old jobs if volume grows.
- Heavy job traffic on your main database can slow your web queries. If this happens, use a separate database or move to Redis.

**Decision rule**
1. If you already run Postgres only, start with `pg-boss` or Graphile Worker.
2. If you already run Redis, or need delays, rate limits, and high volume, use BullMQ.
3. If you are unsure, choose Postgres. Moving a queue later is easy if you wrap enqueue calls in one small module.
