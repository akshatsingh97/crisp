# Runbook: Disk usage over 90% on the database host

**Rule:** Never delete or move files in `pg_wal` by hand. WAL (write-ahead log, the change journal Postgres needs for recovery) must be removed only by Postgres. Manual deletion can corrupt the database or break replicas.

Assumptions: the host runs PostgreSQL, and you have shell access and a superuser `psql` session. Adjust paths if your layout differs.

## 1. Find what uses the space

1. Check the filesystems.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Compare the three areas. Look for the one that is largest or has grown fast.
   ```
   sudo du -xsh /var/lib/postgresql /var/lib/postgresql/*/*/pg_wal /var/log/postgresql
   ```
3. Go to the matching section below.

## 2. Logs are large (`/var/log/postgresql`)

1. List files by size.
   ```
   ls -lhS /var/log/postgresql
   ```
2. Compress old rotated logs with `gzip`.
3. Delete the oldest rotated logs only if your retention policy allows it.
4. Do not delete the current log file. Postgres keeps it open, so the space is not freed.
5. Check that log rotation works. Find out why logs grew if the cause is a burst of errors.

## 3. `pg_wal` is large

Do not touch the files. Find out why Postgres keeps them, then fix that cause.

1. Check for an inactive replication slot. A slot makes Postgres keep WAL for a consumer.
   ```sql
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```
2. If a slot is inactive, restore its consumer first.
3. Drop the slot only if you confirm the consumer is gone for good. That replica will need a rebuild.
   ```sql
   SELECT pg_drop_replication_slot('slot_name');
   ```
4. Check for failing WAL archiving. Postgres keeps WAL until it is archived.
   ```sql
   SELECT last_archived_time, last_failed_time, failed_count FROM pg_stat_archiver;
   ```
5. If `failed_count` is rising, fix the `archive_command` target (full disk, bad credentials, unreachable storage).
6. Check for a lagging replica.
   ```sql
   SELECT application_name, state, replay_lag FROM pg_stat_replication;
   ```
7. After you fix the cause, run `CHECKPOINT;`. Postgres then removes old WAL on its own, and `pg_wal` will shrink.

## 4. Data is large (`/var/lib/postgresql`)

1. Find the biggest tables.
   ```sql
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class WHERE relkind = 'r'
   ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. Remove data only with approval from the data owner.
3. Run `VACUUM FULL` only in a maintenance window. It locks the table and needs extra free space while it runs.
4. If you cannot free enough space, grow the disk or escalate to the database owner.

## Risk

If the disk fills completely, Postgres cannot write WAL and will stop. Act quickly, but do not skip the checks above.

## Verify

1. Run `df -h` again. Usage must fall below 90%.
2. Confirm the alert clears.
3. Record the cause and the fix in the incident notes.
