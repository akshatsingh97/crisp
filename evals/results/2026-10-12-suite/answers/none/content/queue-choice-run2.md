Use Postgres, unless you already run Redis or expect high job volume.

- **Why Postgres:** You probably already have it. Jobs can be written in the same transaction as your data, so you never enqueue a job for a change that rolled back. There is one less service to run, back up, and monitor.
- **How to do it:** Use a library built on `SELECT ... FOR UPDATE SKIP LOCKED`, such as `pg-boss` or `graphile-worker`. Do not write your own queue.
- **When Postgres is enough:** Up to a few hundred jobs per second, which fits most small apps.

Choose Redis (with BullMQ) in these cases:
- You already run Redis for caching or sessions.
- You need thousands of jobs per second.
- You need very low latency, or features such as rate limiting and job flows.

Redis needs care with persistence. If you do not enable AOF, a restart can lose queued jobs. Managed Redis also adds cost.

If you pick Postgres and later outgrow it, moving to BullMQ is a small change when your job handlers are plain functions.
