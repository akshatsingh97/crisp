Yes. Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table for the whole build, which can take many minutes on 50 GB.

```sql
SET statement_timeout = 0;
SET maintenance_work_mem = '2GB';
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

## Concurrent build limits

- It takes longer than a plain build because it scans the table twice.
- It cannot run inside a transaction block. Many migration tools wrap migrations in a transaction, so you must turn that off. In Rails, use `disable_ddl_transaction!`.
- It waits for all older transactions to finish. A long-running or idle-in-transaction session can stall it. Check `pg_stat_activity` for these before you start.
- It can fail and leave an INVALID index. A failed unique index still enforces uniqueness on new writes, so clean it up fast.

## Before you start

1. Check free disk. You need space for the final index plus temporary sort files.
2. Test on a staging copy with similar data. This gives you a time estimate.
3. Set `statement_timeout = 0` for the session. A default timeout will cancel the build.
4. Raise `maintenance_work_mem` for the session only. Do not change it globally.
5. Run the command from a stable session, such as `tmux`. If the connection drops, the build is cancelled.

## During the build

- Expect extra I/O and CPU load. Watch your latency dashboards.
- The build generates a lot of WAL. Watch replication lag on replicas.
- On Postgres 12 and later, track progress with `pg_stat_progress_create_index`.
- On Postgres 11 and later, parallel workers speed up the build. Tune `max_parallel_maintenance_workers` if needed, but they add load.

## After the build

1. Check that the index is valid.

   ```sql
   SELECT indexrelid::regclass, indisvalid
   FROM pg_index
   WHERE indrelid = 'orders'::regclass;
   ```

2. If `indisvalid` is false, drop the index and retry.

   ```sql
   DROP INDEX CONCURRENTLY idx_orders_customer_id;
   ```

3. Confirm with `EXPLAIN` that your target queries use the new index.

## Ways to reduce cost

- If queries filter on a subset of rows, use a partial index with a `WHERE` clause. It builds faster and takes less space.
- Every new index adds some cost to inserts and updates. Make sure the index earns its place.
