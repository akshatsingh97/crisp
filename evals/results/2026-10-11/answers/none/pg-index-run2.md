Yes, a few things matter on a table that size.

## Use `CREATE INDEX CONCURRENTLY`
A plain `CREATE INDEX` takes a `SHARE` lock, which blocks all writes for the whole build. On 50 GB that could be many minutes. `CONCURRENTLY` allows reads and writes to continue.

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id ON orders (customer_id);
```

## Caveats of `CONCURRENTLY`
- **It can't run inside a transaction block.** Some migration tools wrap everything in a transaction. You may need to disable that (e.g. `disable_ddl_transaction!` in Rails, or `atomic = False` in Django).
- **It can fail and leave an invalid index.** This happens on a deadlock, a uniqueness violation, or if you cancel the build. Check for it:
  ```sql
  SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
  ```
  Then `DROP INDEX CONCURRENTLY` it and retry. Don't leave invalid indexes around, because they still add write overhead.
- **It's slower.** It does two table scans and waits for old transactions to finish, so expect roughly 2–3x the time of a plain build.
- **Long-running transactions stall it.** The build waits on any open transaction that predates it, and a stuck one blocks the finish. Check `pg_stat_activity` for old transactions before you start.

## Resource and operational concerns
- **Disk space:** you need room for the new index plus temporary sort files. Check free space first.
- **I/O and CPU load:** the build will compete with production traffic. Run it off-peak if you can.
- **Memory:** raise `maintenance_work_mem` for the session (e.g. `SET maintenance_work_mem = '2GB';`). This speeds up the sort a lot.
- **Parallel workers:** `max_parallel_maintenance_workers` can speed up B-tree builds, but it uses more resources.
- **Replication lag:** the build generates a lot of WAL. Watch replicas, and watch for WAL volume or disk growth on the primary.
- **Timeouts:** make sure `statement_timeout` and `lock_timeout` in your session or role won't kill the build. Set `statement_timeout = 0` for that session. `lock_timeout` is still useful for the brief lock acquisitions at the start and end.

## Before and during the build
1. **Test on a restored copy or staging** with similar data volume to get a time estimate.
2. **Confirm the index helps.** Run `EXPLAIN (ANALYZE, BUFFERS)` on the target queries first. Consider partial indexes (`WHERE ...`) or `INCLUDE` columns to keep the index smaller.
3. **Monitor progress:**
   ```sql
   SELECT phase, blocks_done, blocks_total, tuples_done, tuples_total
   FROM pg_stat_progress_create_index;
   ```
4. **Run it from a stable session** (`tmux`, a bastion host, or a job runner) so a dropped connection doesn't kill it.
5. **Run `ANALYZE` afterward** if the planner doesn't pick up the new index right away.

## If it's a unique index or constraint
Build the unique index concurrently first. Then attach it:
```sql
ALTER TABLE t ADD CONSTRAINT t_col_key UNIQUE USING INDEX idx_name;
```
This avoids a long lock.

If you tell me the Postgres version, the table's write rate, and whether it's partitioned, I can tailor this. Partitioned tables need a different approach, because `CONCURRENTLY` isn't supported on the parent.
