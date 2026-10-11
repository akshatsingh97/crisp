Yes, mostly around locking and failure modes.

## Use `CREATE INDEX CONCURRENTLY`

A plain `CREATE INDEX` takes a lock that blocks all writes (INSERT/UPDATE/DELETE) for the whole build. On 50 GB that could be many minutes. `CONCURRENTLY` lets writes continue.

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

Trade-offs of `CONCURRENTLY`:
- It's slower, because it does two table scans and waits for in-flight transactions.
- It can't run inside a transaction block. Many migration tools wrap migrations in a transaction by default, so you'll need to turn that off for this one. In Rails that's `disable_ddl_transaction!`, and in Flyway it's a non-transactional migration.
- It can fail and leave an **invalid index**. See below.

## Check for invalid indexes after it finishes

If it's cancelled, deadlocks, or hits a unique violation, Postgres leaves behind an index marked invalid. It still adds write overhead but is never used for queries.

```sql
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
```

If you find one, run `DROP INDEX CONCURRENTLY` on it and retry.

## Things that can hurt production

- **Long-running transactions block the build.** The concurrent build waits for older transactions to finish, and so does everything queued behind it. Check `pg_stat_activity` for old open transactions or idle-in-transaction sessions first.
- **I/O and CPU load.** A 50 GB scan will compete with your normal traffic. Run it off-peak and watch disk I/O and latency.
- **Replication lag.** The index build generates a lot of WAL. Watch replica lag, and make sure you have disk headroom for WAL.
- **Disk space.** You need room for the finished index (often 10–30% of the table size, depending on the column) plus temporary sort files.
- **Bloat on a busy table.** Concurrent builds on heavily updated tables can leave more dead tuples to deal with later.

## Tuning the build

Raise `maintenance_work_mem` for your session (e.g. `1GB` or more, within what RAM allows). It speeds up the sort a lot.

```sql
SET maintenance_work_mem = '2GB';
SET max_parallel_maintenance_workers = 4;  -- PG 11+, parallel B-tree builds
```

Parallel workers do work with `CONCURRENTLY` on B-tree indexes. Keep the count modest so you don't starve production queries.

## Safety rails

```sql
SET lock_timeout = '5s';        -- don't queue behind a lock and block others
SET statement_timeout = 0;      -- but don't let a global timeout kill the build
```

`lock_timeout` matters because even `CONCURRENTLY` needs brief locks at the start and end. If it waits on one, it can stall other queries behind it.

## Other tips

- **Test on a restored copy or staging** with similar data size first, to get a time estimate.
- **Monitor progress** (PG 12+) with `pg_stat_progress_create_index`.
- **Partial or covering indexes** are worth considering. If queries only touch a subset of rows, `WHERE` on the index makes it smaller and faster to build.
- **Unique indexes**: if existing duplicates exist, the build fails after doing all the work. Check for duplicates first.
- **Partitioned tables**: `CONCURRENTLY` isn't supported on the parent. Build on each partition, then attach.

If you tell me your Postgres version, the column(s), and how write-heavy the table is, I can tailor this further.
