Use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table until it finishes, and on 50 GB that can take many minutes.

```sql
SET lock_timeout = '5s';
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

The concurrent build lets reads and writes continue, but it has costs. It scans the table twice and waits for all older transactions to finish, so it is slower than a plain build. A single long-running transaction (open for hours, for example) can stall it. Before you start, look in `pg_stat_activity` for old transactions and end or wait for them.

The command cannot run inside a transaction block. Many migration tools wrap each migration in a transaction by default, so turn that off for this one. In Rails, for example, you add `disable_ddl_transaction!`.

If the build fails or you cancel it, Postgres leaves behind an invalid index that still slows down writes. You can find it with this query:

```sql
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
```

Drop it with `DROP INDEX CONCURRENTLY`, then try again. This also happens with a unique index when duplicate values exist, so check for duplicates first.

The build uses a lot of disk, I/O, and CPU. Make sure that you have free space for the new index plus temporary sort files, which is often 20 to 40 percent of the table size. Raise `maintenance_work_mem` for your session (for example to 1GB or 2GB) to speed up the sort. Postgres can also use parallel workers, which you control with `max_parallel_maintenance_workers`. The index writes a large amount of WAL (the write-ahead log, which replicas replay), so watch replication lag and run the build in a quiet period if you can.

If the table is partitioned, `CONCURRENTLY` does not work on the parent table. Build the index on each partition separately, then create the index on the parent so that Postgres attaches them.

Last, try the whole procedure on a staging copy of similar size first. That gives you a realistic build time and shows you any surprises before they reach production.
