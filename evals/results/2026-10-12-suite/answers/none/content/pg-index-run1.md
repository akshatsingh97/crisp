Yes. Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table until the build finishes, which can take minutes to hours on 50 GB.

```sql
SET statement_timeout = 0;
SET maintenance_work_mem = '2GB';
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

What to watch for:

1. **Transactions.** `CONCURRENTLY` cannot run inside a transaction block. Many migration tools wrap each migration in a transaction, so turn that off for this migration.
2. **Failed builds.** A failure, cancel, or timeout leaves an `INVALID` index that still slows writes. Find it with `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`. Then run `DROP INDEX CONCURRENTLY` and try again.
3. **Long transactions.** The build waits for older open transactions to finish. One idle-in-transaction session can stall it for hours. Check `pg_stat_activity` first.
4. **Timeouts.** A default `statement_timeout` can kill the build. Set it to 0 for this session. Also set a short `lock_timeout` so the build does not queue behind a blocked lock.
5. **Disk and I/O.** You need space for the finished index plus temporary sort files. The build also scans the table twice, so expect it to take 2 to 3 times longer than a plain build and to add load.
6. **Replicas.** The build produces a lot of WAL. Watch replica lag and free WAL disk space.
7. **Unique indexes.** If duplicates exist, the build fails and leaves an invalid index. Check for duplicates first.
8. **Partitioned tables.** You cannot use `CONCURRENTLY` on the parent. Build the index on each partition, then attach them.

To watch progress, query `pg_stat_progress_create_index`. If you can, time the build on a restored copy first. After it finishes, confirm that `indisvalid` is true and that `EXPLAIN` uses the new index.
