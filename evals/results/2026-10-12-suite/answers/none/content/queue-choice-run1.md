Use Postgres, if you already run it and expect fewer than about 1,000 jobs per second. Use Redis with BullMQ if you already run Redis, or need very high throughput.

**Why Postgres fits a small app**
- You add no new service to run, back up, or monitor.
- You can enqueue a job in the same transaction as your data change. A job never exists without its row, and a row never exists without its job.
- `FOR UPDATE SKIP LOCKED` lets many workers take jobs safely. Libraries such as `pg-boss` and Graphile Worker handle retries, delays, and schedules for you.

**Why Redis fits other cases**
- BullMQ gives you rate limiting, job priorities, and flows with parent and child jobs. It also has a good dashboard ecosystem.
- Redis handles high job volume with less load than a polling table.
- You must set it up so jobs survive a restart. Turn on AOF persistence and set `maxmemory-policy noeviction`. Otherwise Redis can drop queued jobs when memory is full.

**Watch for these**
- A Postgres queue with heavy churn needs regular vacuuming, or the table bloats. The libraries above manage this, but check it.
- With Redis, a job and your database write are not atomic. You must make jobs idempotent, because a crash between the two steps can lose or repeat a job.
- Both options deliver "at least once", so write every job to be safe to run twice.

Do not add Redis only for the queue. Start with Postgres, and move to Redis when you measure a real limit.
