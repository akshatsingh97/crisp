Use Postgres if your app already uses it and you expect fewer than about 100 jobs per second. Use Redis with BullMQ if you need higher throughput or already run Redis.

Why Postgres fits a small app:
- It adds no new service to run, monitor, or back up.
- You can enqueue a job in the same transaction as your data change. This prevents a job from existing without its data, or the reverse.
- Jobs survive restarts, and you can query them with plain SQL.
- Libraries such as pg-boss and Graphile Worker handle retries, scheduling, and concurrency. They use `SELECT ... FOR UPDATE SKIP LOCKED` (a row lock that skips rows other workers hold).

Why Redis fits other cases:
- It handles very high job volume with low latency.
- BullMQ gives you delayed jobs, rate limits, priorities, and a mature ecosystem.
- Redis needs a new service. Without persistence settings (AOF, an append-only log), a crash can lose jobs. Check your hosting provider's defaults.

Risks to watch:
- Postgres queues add write load and table bloat. Delete or archive finished jobs regularly.
- Long-running transactions in the same database can slow queue polling.
- In Redis, a job can run twice after a worker crash. Make your jobs idempotent (safe to run more than once). This also applies to Postgres queues.

If you are unsure, start with pg-boss or Graphile Worker. You can move to BullMQ later if throughput becomes a problem. Keep your job handlers separate from the queue library to make that move easy.
