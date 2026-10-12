Use Postgres if your app already runs on it and your job volume is under about 100 jobs per second. Use Redis if you need higher throughput or low-latency delays.

**Why Postgres fits a small app**
- You add no new service to run, monitor, or back up.
- Jobs can be enqueued in the same transaction as your data. This prevents lost or phantom jobs.
- `SELECT ... FOR UPDATE SKIP LOCKED` lets many workers claim jobs without blocking each other.
- Failed jobs, retries, and history are easy to inspect with plain SQL.
- Libraries for Node.js: `pg-boss` and `graphile-worker`.

**Why Redis fits some apps**
- It handles thousands of jobs per second with very low latency.
- It has mature features: delayed jobs, rate limits, priorities, and repeatable jobs.
- Library for Node.js: `BullMQ`. It has a good dashboard ecosystem.

**Risks**
- Redis can lose jobs on a crash if persistence is off or set to periodic snapshots. Enable AOF (append-only file logging) and set `maxmemory-policy noeviction`. Otherwise Redis can evict queue keys when memory is full.
- Redis is a second system to host and secure. Managed Redis adds cost.
- Postgres queues add write load and table bloat on your main database. Heavy queue traffic can slow your app queries. Run frequent vacuum, delete old completed jobs, or use a separate database.
- Postgres polling adds some latency. `pg-boss` and `graphile-worker` reduce this with `LISTEN/NOTIFY`.

**How to decide**
1. If you already use Redis for caching or sessions, and you need fast jobs, choose BullMQ.
2. If you only have Postgres, start with `pg-boss` or `graphile-worker`.
3. If you need transactional enqueue (for example, create a user and queue a welcome email atomically), choose Postgres.

You can migrate later. Keep your job handlers independent of the queue library, so switching costs little.
