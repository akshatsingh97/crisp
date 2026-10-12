Yes. Use `CREATE INDEX CONCURRENTLY`. A plain `CREATE INDEX` blocks all writes to the table until the build ends, which on 50 GB can take many minutes.

```sql
SET maintenance_work_mem = '2GB';          -- this session only
SET statement_timeout = 0;
CREATE INDEX CONCURRENTLY idx_orders_customer ON orders (customer_id);
```

**What to watch for**

1. **Run it outside a transaction.** `CONCURRENTLY` fails inside a `BEGIN` block. Some migration tools wrap each migration in a transaction. Turn that off for this one.
2. **A failed build leaves an invalid index.** It still slows writes. Find it with `SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;`. Then run `DROP INDEX CONCURRENTLY` on it and retry. A failed unique index still enforces uniqueness on new rows.
3. **Long transactions stall the build.** It waits for every transaction that started before it. It also holds back vacuum cleanup while it runs. Check `pg_stat_activity` for old or idle-in-transaction sessions first.
4. **Check disk space.** You need room for the finished index and for temporary sort files. A rough guide is 10 to 30% of the table size, depending on the columns. Test the real size on a restored copy.
5. **Expect extra load.** The build reads the table twice, so it is slower than a plain build. It also creates a lot of WAL. Watch replication lag and WAL archive space. Run it in a quiet period.
6. **Tune the session.** A higher `maintenance_work_mem` speeds the sort. `max_parallel_maintenance_workers` (Postgres 11 and later) allows parallel workers. Keep both within what production can spare.
7. **Partitioned tables are different.** You cannot use `CONCURRENTLY` on the parent. Build the index on each partition, then create the parent index with `ON ONLY` and attach the partition indexes.

**Monitor and verify**

- Progress: `SELECT * FROM pg_stat_progress_create_index;`
- After it finishes, confirm `indisvalid` is true. Then run `ANALYZE` on the table and check with `EXPLAIN` that your query uses the index.

If you share the column types, your Postgres version, and whether you use partitions or replicas, I can tailor these steps. I can also estimate the index size.
