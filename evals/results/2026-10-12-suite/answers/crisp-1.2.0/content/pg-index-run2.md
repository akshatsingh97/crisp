Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes (INSERT, UPDATE, DELETE) on the table until it finishes. On 50 GB, that can take many minutes.

## Before you start

1. Check free disk space. The index needs room for its final size, plus temporary sort files.
2. Find long-running transactions with `SELECT pid, xact_start, state, query FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY xact_start;`. The concurrent build waits for older transactions to end. One stuck transaction can stall it for hours.
3. Set `maintenance_work_mem` for your session, for example `SET maintenance_work_mem = '2GB';`. A larger value speeds up the sort.
4. Set `max_parallel_maintenance_workers` (Postgres 11 and later) if you have spare CPU. It speeds up B-tree builds.
5. Run `SET lock_timeout = '5s';` so the build gives up fast if it cannot get its brief locks. Retry later.
6. Set `statement_timeout = 0` for this session. A default timeout will kill the build partway through.

## Run the build

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

Watch progress in another session:

```sql
SELECT phase, blocks_done, blocks_total, tuples_done, tuples_total
FROM pg_stat_progress_create_index;
```

## What to watch for

- `CONCURRENTLY` cannot run inside a transaction block. Many migration tools wrap each migration in a transaction. Turn that off for this migration. In Rails, use `disable_ddl_transaction!`. In Flyway, use `executeInTransaction=false`.
- The build scans the table twice and waits for old transactions between scans. It will take longer than a plain build, often two to three times.
- It adds heavy read and write load. Run it in a quiet period and watch CPU, I/O, and replication lag. Replicas must replay the build too.
- Temporary files and WAL (write-ahead log) volume grow during the build. Check that WAL archiving and replica disks can handle it.
- Do not cancel and forget. A failed or cancelled build leaves an INVALID index that still slows writes. Check with `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`. Then run `DROP INDEX CONCURRENTLY idx_name;` and retry.
- A unique index can fail if duplicate rows exist, or if a duplicate arrives during the build. The failed index stays INVALID. Clean the data first, then retry.
- Partitioned tables do not support `CONCURRENTLY` on the parent. Build the index on each partition concurrently. Then create the parent index with `ON ONLY` and attach the partition indexes.

## After the build

1. Confirm `indisvalid` is true for the new index.
2. Run `ANALYZE tablename;` so the planner has fresh statistics.
3. Run `EXPLAIN` on your target query to confirm it uses the index.
4. Check for redundant older indexes. Drop them with `DROP INDEX CONCURRENTLY` to save write cost and disk.

If you cannot accept the extra load or duration, test the exact build on a restored copy first. That gives you a real time estimate. The right settings depend on your hardware, which I do not know.
