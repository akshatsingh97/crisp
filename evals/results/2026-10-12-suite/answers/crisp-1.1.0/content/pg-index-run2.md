Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table for the whole build, which on 50 GB can take many minutes.

Why the concurrent build is safer:
- It allows reads and writes during the build.
- It takes longer, because it scans the table twice.
- It waits for old open transactions to finish, so one long transaction can stall it.

Before you start:
1. Check for long-running transactions in `pg_stat_activity`. Cancel or wait for them.
2. Check free disk space. The index needs room, and sorting can use temporary space too.
3. Set `lock_timeout` for the session, for example `SET lock_timeout = '5s';`. This stops the brief lock steps from queuing behind other queries and blocking traffic.
4. Raise `maintenance_work_mem` for the session to speed up the sort. Pick a value your server memory can support.
5. Set `statement_timeout = 0` for the session. A default timeout can kill the build partway.

Run the build:
1. Run `CREATE INDEX CONCURRENTLY idx_name ON tbl (col);` outside a transaction block. It fails inside `BEGIN ... COMMIT`.
2. If you use a migration tool, turn off its automatic transaction for this migration. In Rails, use `disable_ddl_transaction!`.
3. Watch progress with `SELECT * FROM pg_stat_progress_create_index;`.

Risks to know:
- If the build fails or you cancel it, Postgres leaves an `INVALID` index. It still slows writes. Find it with `\d tbl` or `pg_index.indisvalid`, then run `DROP INDEX CONCURRENTLY idx_name;` and retry.
- A unique index can fail if duplicate rows exist, and it leaves an invalid index too.
- The build adds heavy I/O and CPU load. Run it in a quiet period and watch replication lag on replicas.
- On a partitioned table, `CONCURRENTLY` does not work on the parent. Build the index on each partition, then attach them.

After the build, confirm `indisvalid` is true. Then run `ANALYZE tbl;` so the planner uses the new index well.
