Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table until it finishes, which on 50 GB can take many minutes.

```sql
SET statement_timeout = 0;
SET maintenance_work_mem = '2GB';
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

## Limits of CONCURRENTLY

- It cannot run inside a transaction block. If your migration tool wraps migrations in a transaction, disable that for this migration. Rails uses `disable_ddl_transaction!`. Django uses `atomic = False`.
- It is slower than a plain build. It scans the table twice and waits for all older transactions to finish.
- A long-running or idle-in-transaction session will stall the build. Check `pg_stat_activity` first and end stuck sessions.
- It can fail and leave an `INVALID` index. This happens on deadlock, cancel, or a uniqueness violation. The invalid index still slows down writes.
- On a partitioned table, you cannot use `CONCURRENTLY` on the parent. Build the index on each partition, then create the parent index with `ON ONLY` and attach the partition indexes.

## Before you start

1. Check free disk space. The index needs roughly its final size, and the build can use temporary sort space on top of that.
2. Check for long transactions: `SELECT pid, state, xact_start FROM pg_stat_activity WHERE xact_start < now() - interval '5 minutes';`
3. Set `statement_timeout = 0` for the session. A default timeout will kill the build partway through.
4. Raise `maintenance_work_mem` for the session only. Higher values speed up the sort. Do not set it globally.
5. If you have replicas, expect extra WAL and replication lag. Watch lag during the build.
6. Run the build off-peak. It adds I/O and CPU load, and it makes writes slightly slower while it runs.
7. If you can, rehearse on a staging copy of similar size to get a time estimate.

## While it runs

Watch progress with `pg_stat_progress_create_index`. It shows the phase, blocks scanned, and tuples processed.

## After it finishes

1. Confirm the index is valid: `SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'idx_orders_customer_id'::regclass;`
2. If `indisvalid` is false, run `DROP INDEX CONCURRENTLY idx_orders_customer_id;` and retry. Find the cause first. A unique index fails if duplicates exist.
3. Run `ANALYZE orders;` so the planner uses the new index with good statistics.
4. Check with `EXPLAIN` that your target query uses the index.

If the build is too slow or too heavy, one option is to build on a replica or restored copy first. This only helps if you can then promote it, so it suits migrations with a planned failover.
