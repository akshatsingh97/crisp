Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table until it finishes, which on 50 GB can take many minutes.

```sql
SET statement_timeout = 0;
SET maintenance_work_mem = '2GB';
CREATE INDEX CONCURRENTLY idx_name ON tbl (col);
```

## Risks of CONCURRENTLY

- It cannot run inside a transaction block. Many migration tools wrap migrations in a transaction. Turn that off for this migration (for example, `disable_ddl_transaction!` in Rails).
- It scans the table twice and waits for older transactions to finish. It takes longer than a plain build, often 2 to 3 times.
- A long-running open transaction, even an idle one, can stall the build. Check `pg_stat_activity` for old transactions before you start.
- If it fails or you cancel it, Postgres leaves an INVALID index. That index still slows writes.
- A unique index fails if duplicate values exist or appear during the build. It also leaves an INVALID index.
- It holds a `SHARE UPDATE EXCLUSIVE` lock. This blocks other schema changes on the table. It also blocks manual VACUUM, and autovacuum may cancel itself.

## Resource cost

- Disk: you need room for the final index plus temporary sort files. Check free space first.
- I/O and CPU: the build competes with production traffic. Run it off-peak.
- WAL (write-ahead log): the build generates a lot of it. Watch replication lag on replicas and disk on the primary.
- Memory: a higher `maintenance_work_mem` speeds the sort. Do not set it so high that it risks out-of-memory with other sessions.
- Parallelism: on Postgres 11 or later, `max_parallel_maintenance_workers` can speed the build. It adds more load.

## Steps

1. Test the exact statement on a staging copy of similar size. Note the duration.
2. Confirm the index is worth it. A partial index (`WHERE ...`) or fewer columns can cut size and write cost.
3. Check for old transactions and free disk space.
4. Run the statement in a session with `statement_timeout = 0`. Use `psql` or a terminal multiplexer so a dropped connection does not kill it.
5. On Postgres 12 or later, watch progress with `pg_stat_progress_create_index`.
6. When it finishes, confirm the index is valid:

```sql
SELECT indexrelid::regclass, indisvalid
FROM pg_index
WHERE indrelid = 'tbl'::regclass;
```

## If it fails

1. Find the INVALID index with the query above.
2. Run `DROP INDEX CONCURRENTLY idx_name;`
3. Fix the cause, such as duplicates or a blocking transaction.
4. Run the build again.

Run `ANALYZE tbl;` afterward if the planner does not pick up the new index. Run `EXPLAIN` on your target query to confirm the index is used.
