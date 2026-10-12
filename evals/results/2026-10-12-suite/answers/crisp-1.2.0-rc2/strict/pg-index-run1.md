Yes. Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table until it finishes, which on 50 GB can take many minutes.

```sql
SET statement_timeout = 0;
SET lock_timeout = '5s';
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

Risks and limits of the concurrent build:

1. The command cannot run inside a transaction block. Many migration tools wrap each migration in a transaction. Turn that off for this migration. For example, in Rails use `disable_ddl_transaction!`.
2. The build is slower than a plain build. It scans the table two times and waits for older transactions to finish.
3. A long-running open transaction can stall the build. Check `pg_stat_activity` for old transactions before you start.
4. If the build fails or you cancel it, Postgres leaves an INVALID index. It still slows writes. Find it with `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`. Drop it with `DROP INDEX CONCURRENTLY`, then retry.
5. A unique index can fail on duplicate rows. Check for duplicates first.
6. Set `lock_timeout` so the command does not queue behind a lock and block other queries. If it times out, retry later.
7. A default `statement_timeout` can kill the build. Set it to 0 for the session, as in the example.

Resource load:

- Make sure that you have free disk space for the new index. A rough guide is 10 to 30 percent of the table size. It depends on the column types.
- Expect extra I/O and CPU. The build also creates WAL (write-ahead log) that can increase replica lag. Watch replication lag during the build.
- Raise `maintenance_work_mem` for the session, for example to 1GB or more, to speed up the sort. Make sure that the server has enough RAM.
- Parallel build is available. Tune `max_parallel_maintenance_workers` if the server has spare cores.

Monitoring and validation:

- Watch progress with `pg_stat_progress_create_index`.
- After the build, make sure that `indisvalid` is true.
- Run `ANALYZE` on the table and check with `EXPLAIN` that the planner uses the new index.
- Test the whole procedure first on a staging copy of similar size, if you can.

If the table is partitioned, `CONCURRENTLY` does not work on the parent table. Create the index on each partition concurrently. Then create the parent index with `CREATE INDEX ... ON ONLY parent`, and attach each partition index with `ALTER INDEX ... ATTACH PARTITION`.
