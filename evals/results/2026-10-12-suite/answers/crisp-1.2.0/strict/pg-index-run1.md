Yes. Use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table until the build ends. On 50 GB, that can mean minutes to hours of blocked inserts, updates, and deletes.

Reads continue during both kinds of build.

## What CONCURRENTLY costs

- The build reads the table twice and waits for older transactions. It is often 2 to 3 times slower.
- It uses more CPU and I/O.
- It cannot run inside a transaction block. Many migration tools wrap each migration in a transaction. Turn that off for this migration (for example, `disable_ddl_transaction!` in Rails).

## Before you start

1. Check free disk space. You need room for the final index and for temporary sort files.
2. Look for long-running transactions. The build must wait for them to finish, and one old transaction can stall it. Run:
   ```sql
   SELECT pid, state, xact_start, query
   FROM pg_stat_activity
   WHERE xact_start < now() - interval '5 minutes'
   ORDER BY xact_start;
   ```
3. Set session parameters. Use a `lock_timeout` so the build does not queue behind a lock and block other queries. Remove `statement_timeout` for this session. Raise memory.
   ```sql
   SET lock_timeout = '5s';
   SET statement_timeout = 0;
   SET maintenance_work_mem = '2GB';
   SET max_parallel_maintenance_workers = 4;
   ```
   The values are examples. Pick numbers that fit your server.
4. Run the build in a stable session, such as `tmux` on a bastion host. If the connection drops, the build stops.
5. Pick a low-traffic window. If you can, time the build first on a restored copy.

## Run and monitor

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

From another session, watch progress (Postgres 12 and later):

```sql
SELECT phase, blocks_done, blocks_total FROM pg_stat_progress_create_index;
```

Also watch replication lag. The build creates a large volume of WAL (write-ahead log), and replicas must replay all of it.

## If the build fails

A failed or cancelled concurrent build leaves an invalid index. It still adds write overhead. Find it and drop it:

```sql
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
DROP INDEX CONCURRENTLY idx_orders_customer_id;
```

Then fix the cause and retry. For a unique index, the usual cause is duplicate data. An invalid unique index still rejects new duplicates.

## Other options

- Use a partial index (`WHERE` clause) if queries touch only a subset of rows. The index will be smaller and faster to build.
- After the build, confirm the planner uses the index with `EXPLAIN (ANALYZE)` on your target query.
