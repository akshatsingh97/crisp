Yes, use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table until it finishes. On 50 GB, that can take many minutes.

The concurrent build lets reads and writes continue. It costs more: it scans the table twice and takes longer overall.

Steps:

1. Check for long-running transactions in `pg_stat_activity`. The build waits for them to finish, so one old transaction can stall it.
2. Check free disk space. The index needs room, and a sort can spill temporary files to disk.
3. In the session, set `maintenance_work_mem` higher, for example `1GB`. This speeds up the sort.
4. Set `lock_timeout` to a few seconds. The build then fails fast instead of queueing behind a lock and blocking other queries.
5. Run `CREATE INDEX CONCURRENTLY idx_name ON tbl (col);` outside a transaction block. It will fail inside one.
6. Watch progress in `pg_stat_progress_create_index`.
7. After it finishes, confirm `indisvalid` is true for the index in `pg_index`.

Risks:

- If the build fails or you cancel it, Postgres leaves an `INVALID` index. It still slows writes. Run `DROP INDEX CONCURRENTLY idx_name;` and try again.
- Migration tools often wrap each migration in a transaction. Turn that off for this migration. In Rails, use `disable_ddl_transaction!`.
- A `UNIQUE` index fails if duplicate rows exist, or if a writer inserts one during the build. You will get an `INVALID` index.
- The build adds heavy I/O and WAL (write-ahead log) volume. Replicas can lag, so watch replication lag during the build.
- Run it in a quiet period if you can. Test on a restored copy first to get a time estimate.

The time depends on your hardware and load, so I cannot give a number.
