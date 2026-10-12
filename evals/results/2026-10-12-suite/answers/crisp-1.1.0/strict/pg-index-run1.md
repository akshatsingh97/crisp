Yes, use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table during the build. On 50 GB, that can last many minutes or hours.

The concurrent build has its own risks:

- It cannot run inside a transaction block. Many migration tools wrap each migration in a transaction, so turn that off for this one. In Rails, use `disable_ddl_transaction!`.
- It scans the table twice and waits for older transactions to finish. One long-running transaction can stall the build. Check `pg_stat_activity` first.
- If the build fails or you cancel it, it leaves an INVALID index (a broken index that Postgres will not use). That index still slows writes. Run `DROP INDEX CONCURRENTLY` on it, then retry.
- A UNIQUE index build fails if the table has duplicate values. It also leaves an invalid index.
- The build takes longer than a plain build and adds heavy disk I/O. It also writes a lot of WAL (the log of all changes), so replicas can lag.

Steps:

1. Make sure that free disk space can hold the final index plus temporary sort files.
2. Check for old transactions: `SELECT pid, xact_start, state FROM pg_stat_activity WHERE xact_start < now() - interval '5 minutes';`
3. In the same session, set `lock_timeout = '5s'`. This stops the short locks at the start and end from queuing behind other work.
4. Raise `maintenance_work_mem` for the session, for example `SET maintenance_work_mem = '2GB';`. Pick a value that fits your server memory.
5. Run `CREATE INDEX CONCURRENTLY idx_name ON tbl (col);`
6. Watch progress in `pg_stat_progress_create_index`. Also watch replica lag.
7. Make sure that the index is valid: `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;` The new index must not appear.

If possible, run the build in a low-traffic window. Test the same command on a staging copy of similar size to measure the duration.
