Use Postgres if your app already uses it. Add Redis only if you need very high job volume or you already run Redis.

**Why Postgres fits a small app**
- You add no new service to run, monitor, or back up.
- You can add a job in the same transaction as your data change. If the transaction fails, the job does not exist. Redis cannot do this.
- Jobs stay safe on disk with your normal backups.
- You can query jobs with plain SQL.
- Libraries do the hard work. Use `pg-boss` or `graphile-worker`. Both use `FOR UPDATE SKIP LOCKED`, which lets many workers take different rows without blocking each other.
- Postgres handles hundreds of jobs per second. This is enough for most small apps.

**When Redis is the better choice**
- You need thousands of jobs per second or more.
- You need strong rate limiting, job priorities, or flow control between jobs. Use `BullMQ`, which is the standard Node.js queue on Redis.
- You already run Redis for cache or sessions.
- Queue traffic would load your main database too much.

**Risks to know**
- Postgres: a high job rate causes table bloat (dead rows that take space). Tune autovacuum and delete old jobs.
- Postgres: long transactions in workers can hold locks and slow the queue. Keep job work outside the claim transaction.
- Redis: by default it can lose recent jobs after a crash. Turn on AOF persistence (an append-only log on disk) and check your provider settings.
- Redis: you cannot make a job and a database write atomic. You must handle duplicate or lost jobs yourself, for example with idempotent job handlers.

**Migration path**
Start with Postgres. If load grows, move to BullMQ later. Keep your job handlers independent of the queue library, so the switch is small.
