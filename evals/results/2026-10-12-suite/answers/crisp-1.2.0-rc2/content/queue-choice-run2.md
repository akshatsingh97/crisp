Use Postgres if your app already runs it and you expect fewer than a few hundred jobs per second. Use Redis if you need higher throughput or already run it.

**Why Postgres fits a small app**
- It adds no new service to run, monitor, or back up.
- You can enqueue a job in the same transaction as your data change. This prevents lost or phantom jobs.
- `SELECT ... FOR UPDATE SKIP LOCKED` lets many workers claim jobs without blocking each other.
- Ready libraries exist: pg-boss and Graphile Worker. Both handle retries, scheduling, and delayed jobs.

**Why Redis fits other cases**
- It has lower latency and higher throughput.
- BullMQ is mature. It offers priorities, rate limiting, repeatable jobs, and a dashboard ecosystem.
- Set `maxmemory-policy noeviction` and enable AOF (append-only file persistence). Otherwise Redis can drop queued jobs.

**Risks**
- Postgres: heavy job churn creates dead rows (deleted rows awaiting cleanup). Tune autovacuum and delete finished jobs often.
- Postgres: workers poll for jobs, so latency can reach about a second. LISTEN/NOTIFY can reduce this.
- Redis: you now run a second datastore. Enqueuing is not transactional with your database, so a crash between the two writes can lose or duplicate a job. Make jobs idempotent (safe to run twice).

**Decision rule**
1. If you already use Postgres and have no Redis, start with pg-boss or Graphile Worker.
2. If you already use Redis, or need high volume or sub-100ms pickup, use BullMQ.
3. If your volume grows later, you can move the queue to Redis. Keep job handlers behind a small interface to make that easy.
