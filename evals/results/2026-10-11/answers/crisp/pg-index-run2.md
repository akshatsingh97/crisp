Yes. Use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table for the whole build.

Before you start:

1. Check free disk space. The build needs room for the full index, and sorting can use temporary files too.
2. Find long-running transactions with `SELECT pid, xact_start, state FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY xact_start;`. The concurrent build waits for them to finish, so end or wait out the old ones.
3. Set `SET lock_timeout = '5s';` in your session. The build takes brief locks at the start and end, and this stops it from queuing behind a blocked statement and stalling other queries.
4. Raise `maintenance_work_mem` for the session, for example `SET maintenance_work_mem = '2GB';`. Use a value your server can afford.
5. Raise `max_parallel_maintenance_workers` if you have spare CPU. This speeds up the build.

Run it:

```sql
CREATE INDEX CONCURRENTLY idx_name ON my_table (my_column);
```

Risks:

- It cannot run inside a transaction block. Many migration tools wrap migrations in a transaction by default. In Rails, use `disable_ddl_transaction!`. Other tools have similar options.
- It scans the table twice, so it takes longer than a normal build. On 50 GB, expect minutes to hours depending on hardware.
- If it fails or you cancel it, Postgres leaves an `INVALID` index behind. It still slows writes. Find it with `\d my_table` or by checking `pg_index.indisvalid`. Remove it with `DROP INDEX CONCURRENTLY idx_name;` and retry.
- For a `UNIQUE` index, duplicate values make the build fail and leave an invalid index.
- The build adds I/O and CPU load and writes extra WAL. Watch replication lag on replicas.
- On a partitioned table, `CONCURRENTLY` does not work on the parent table. Build the index on each partition concurrently, then create the parent index with `ON ONLY` and attach the partition indexes.

To monitor progress, query `pg_stat_progress_create_index`. It shows the current phase and the blocks or tuples processed.

If possible, rehearse on a recent copy of the data first. That gives you a real build time and shows any surprises before production.
