Yes. Use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table until it finishes, and on 50 GB that can take many minutes or more.

The concurrent form lets reads and writes continue. It is slower, because it scans the table twice and waits for open transactions to finish. It also cannot run inside a transaction block, so do not wrap it in `BEGIN` and `COMMIT`. Some migration tools wrap each migration in a transaction by default, so turn that off for this one.

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

A concurrent build can fail and leave an invalid index behind. This happens if it hits a deadlock, a uniqueness violation, or a cancelled session. The invalid index still slows down every write, but the planner will not use it. After the build, run the query below. If `indisvalid` is false, drop the index with `DROP INDEX CONCURRENTLY` and try again.

```sql
SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE indexrelid = 'idx_orders_customer_id'::regclass;
```

A long-running transaction can stall the build, because the build waits for older transactions to finish. Check `pg_stat_activity` for old open transactions before you start, and end any that are stuck.

The build also uses a lot of disk and I/O. Make sure that you have free disk space of at least the expected index size, plus room for temporary files. Watch replication lag if you have replicas, because the build writes a large amount of WAL (the write-ahead log that replicas replay). You can raise `maintenance_work_mem` for your session, for example to 1GB, to speed up the sort. You can also raise `max_parallel_maintenance_workers` if the server has spare CPU.

Run the build in a quiet period if you can, and set `statement_timeout` to 0 for that session so the build is not cut off. You can track progress in the `pg_stat_progress_create_index` view.

If the index is `UNIQUE`, existing duplicate rows will make the build fail, so check for duplicates first. Test the whole procedure on a copy of the data when possible, so you know the rough duration before you run it in production.
