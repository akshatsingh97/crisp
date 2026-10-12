Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table for the whole build. On 50 GB, that can mean tens of minutes of downtime for inserts, updates, and deletes.

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

## Limits of CONCURRENTLY

- It cannot run inside a transaction block. Many migration tools wrap each migration in a transaction. You must turn that off for this migration (for example, `disable_ddl_transaction!` in Rails).
- It is slower than a plain build. It scans the table twice and waits for older transactions to finish.
- A long-running transaction will stall the build, so check `pg_stat_activity` first.
- If the build fails or you cancel it, Postgres leaves an INVALID index. This index still adds write overhead and does nothing for reads.
- A unique index that hits duplicate values also fails this way.

To check for invalid indexes:

```sql
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
```

To clean up, run `DROP INDEX CONCURRENTLY idx_name;` and retry. A plain `DROP INDEX` takes a lock that blocks queries on the table.

## Session settings

Set these in the session that runs the build:

```sql
SET lock_timeout = '5s';
SET statement_timeout = 0;
SET maintenance_work_mem = '2GB';
SET max_parallel_maintenance_workers = 4;
```

- `lock_timeout` stops the build from queuing behind a long lock and blocking other queries. If it fails on timeout, retry.
- `statement_timeout` must be 0 or very high. A low value cancels the build and leaves an invalid index.
- Size `maintenance_work_mem` to your free RAM. A larger value speeds up the sort.
- Parallel workers (Postgres 11 and later) shorten the build but add I/O load.

## Production impact

- Disk: Check free space first. You need room for the full index plus temporary sort files.
- I/O and CPU: The build will compete with your normal traffic. Run it off-peak.
- WAL and replicas: A big index generates a lot of WAL (write-ahead log). Watch replica lag and archive storage.
- Vacuum: A long build holds back the cleanup horizon. Dead rows pile up on busy tables until it finishes.
- Connection: If the client disconnects, the build cancels. Run it from `tmux` or `screen`, or from a host close to the database.

## Monitoring

On Postgres 12 and later, track progress with:

```sql
SELECT phase, blocks_done, blocks_total, tuples_done, tuples_total
FROM pg_stat_progress_create_index;
```

## Before and after

1. Restore a recent backup to a test instance and time the build there.
2. Confirm the index helps with `EXPLAIN (ANALYZE, BUFFERS)` on the target query. Every extra index slows writes.
3. Consider a partial index (`WHERE ...`) or `INCLUDE` columns if they fit your query. They can cut size and build time.
4. After the build, check `indisvalid` and run `ANALYZE tablename;`.

## If the table is partitioned

`CONCURRENTLY` does not work on a partitioned parent table. The steps are:

1. Create the index on the parent with `CREATE INDEX ... ON ONLY parent`. This creates an invalid placeholder.
2. Build each partition's index with `CONCURRENTLY`.
3. Run `ALTER INDEX parent_idx ATTACH PARTITION partition_idx;` for each one.
