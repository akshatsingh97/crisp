Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table for the whole build, which can take many minutes on 50 GB.

Things to watch:

- **No transaction block:** The concurrent form fails inside a transaction. If a migration tool wraps your SQL in a transaction, turn that off for this migration (in Rails, use `disable_ddl_transaction!`).
- **Failed builds leave an invalid index:** If the build fails or you cancel it, Postgres keeps a broken index. Check `pg_index.indisvalid`, then run `DROP INDEX CONCURRENTLY` and retry. Duplicate values in a `UNIQUE` index cause this failure.
- **Long transactions stall the build:** The build waits for every older open transaction to finish. Check `pg_stat_activity` first and end idle-in-transaction sessions.
- **Slower build and more load:** It scans the table twice, so it takes longer than a plain build. Run it in a low-traffic window.
- **Disk space:** Make sure free disk covers the new index plus temporary sort files. Estimate the index size from a similar index.
- **Replication lag:** The build writes a lot of WAL (the write-ahead log). Watch replica lag during the build.
- **Memory and parallelism:** Raise `maintenance_work_mem` for your session, for example to 1GB or more. Parallel workers (`max_parallel_maintenance_workers`) can speed up the build.
- **Lock timeout:** The build takes brief locks at the start and end. Set `lock_timeout` (for example `'5s'`) so it fails fast instead of queuing behind a lock and blocking other queries.

To track progress, query `pg_stat_progress_create_index`. After the build, run `ANALYZE` on the table and confirm the planner uses the index with `EXPLAIN`.
