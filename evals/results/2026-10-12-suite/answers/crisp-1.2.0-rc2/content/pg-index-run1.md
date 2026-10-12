Yes. Use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table for the whole build. On 50 GB, that can mean many minutes of outage.

```sql
SET statement_timeout = 0;
CREATE INDEX CONCURRENTLY idx_name ON tbl (col);
```

## What CONCURRENTLY changes

- It reads the table twice and waits for older transactions, so it takes 2 to 3 times longer.
- It cannot run inside a transaction block. Some migration tools wrap each migration in a transaction. Turn that off for this migration (Rails: `disable_ddl_transaction!`).
- It holds a `SHARE UPDATE EXCLUSIVE` lock. Reads and writes continue. Other schema changes and manual `VACUUM` on that table will wait.

## Risks before you start

1. Check for long-running transactions in `pg_stat_activity`. The build waits for them, and it can appear stuck.
2. Check free disk space. You need room for the full index plus temporary sort files.
3. Expect extra I/O, CPU, and WAL. Replicas can lag, so watch replication lag during the build.
4. Run it in a low-traffic window.
5. Check your session timeouts. A `statement_timeout` or `idle_in_transaction_session_timeout` can kill the build.

## Speed tuning (optional)

- Raise `maintenance_work_mem` for the session, for example `SET maintenance_work_mem = '2GB';`. Keep it within free RAM.
- Raise `max_parallel_maintenance_workers` (Postgres 11+). Parallel builds work for B-tree indexes.

## Monitor progress

```sql
SELECT phase, blocks_done, blocks_total, tuples_done, tuples_total
FROM pg_stat_progress_create_index;
```

This view exists in Postgres 12+.

## If the build fails or you cancel it

A failed concurrent build leaves an INVALID index. It still slows down writes but is never used by queries. Find it:

```sql
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
```

Drop it with `DROP INDEX CONCURRENTLY idx_name;` and run the build again.

A `UNIQUE` index fails if duplicate values exist or arrive during the build. Check for duplicates first.

## After the build

1. Confirm the index shows `indisvalid = true`.
2. Run `ANALYZE tbl;` so the planner knows about the new index.
3. Check with `EXPLAIN` that your target query uses it.

If you can, rehearse on a staging copy of similar size to get a time estimate. I do not know your Postgres version, so check the version notes above.
