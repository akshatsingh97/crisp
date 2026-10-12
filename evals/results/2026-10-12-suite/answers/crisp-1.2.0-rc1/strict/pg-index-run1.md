Yes, use `CREATE INDEX CONCURRENTLY`, because a plain `CREATE INDEX` blocks all writes to the table until the build ends.

A plain build allows reads but blocks INSERT, UPDATE, and DELETE. On 50 GB, that can last many minutes or hours. Your app will queue and time out.

`CONCURRENTLY` keeps writes working. The cost is a slower build, because Postgres scans the table two times.

## Steps

1. Check free disk space. The index needs room, and the sort can use temporary files.
2. Look for long transactions. The build waits for older transactions to end, so one long transaction can stall it.
   ```sql
   SELECT pid, now() - xact_start AS age, state, query
   FROM pg_stat_activity
   WHERE xact_start IS NOT NULL
   ORDER BY age DESC;
   ```
3. Set session values. Make sure that `maintenance_work_mem` fits in free RAM.
   ```sql
   SET maintenance_work_mem = '2GB';
   SET statement_timeout = 0;
   SET lock_timeout = '5s';
   ```
4. Start a session that survives a dropped connection, for example `tmux` or a job runner. If the connection drops, the build cancels.
5. Run the build.
   ```sql
   CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
   ```
6. Watch progress. This view exists in Postgres 12 and later.
   ```sql
   SELECT * FROM pg_stat_progress_create_index;
   ```
7. When the build ends, make sure that the index is valid.
   ```sql
   SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE NOT indisvalid;
   ```
   This query must return no row for your index.

## Risks

- Transaction block: `CONCURRENTLY` cannot run inside a transaction. Postgres returns "cannot run inside a transaction block". Many migration tools wrap each migration in a transaction. Turn that off for this one, for example `disable_ddl_transaction!` in Rails.
- Failed build: a failure or cancel leaves an invalid index. It still slows every write. Drop it with `DROP INDEX CONCURRENTLY idx_orders_customer_id;` and run the build again.
- Unique index: if the data has duplicates, the build fails. The invalid index still enforces uniqueness on new writes until you drop it.
- Replication: the build writes a large amount of WAL (the write-ahead log). Watch replica lag during the build.
- Load: the build adds disk I/O and CPU load. Run it in a low-traffic period.
- Vacuum: a running vacuum on the same table makes the build wait for it.
- Lock timeout: if the build fails on `lock_timeout`, run it again. Nothing is lost.

## Options

- Use a partial index, for example `WHERE status = 'active'`, if your queries filter on a small part of the rows. It is smaller and faster to build.
- Raise `max_parallel_maintenance_workers` (Postgres 11 and later) to speed up the build. This uses more CPU.
- Test the build on a staging copy first. It gives you a time estimate.
- After the build, run `EXPLAIN` on your target query to confirm that the planner uses the index.
