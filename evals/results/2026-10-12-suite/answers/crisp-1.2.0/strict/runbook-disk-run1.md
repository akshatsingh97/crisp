# Runbook: Disk usage over 90% on the database host

**Warning:** Never delete files in `/var/lib/postgresql/.../pg_wal` by hand. PostgreSQL needs these WAL files (write-ahead log) for crash recovery. Manual deletion can corrupt the database and stop it from starting.

## Steps

1. Find the full filesystem.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
   If both paths share one filesystem, treat them as one problem.

2. Find the largest directories.
   ```
   du -xh --max-depth=3 /var/lib/postgresql /var/log/postgresql | sort -h | tail -20
   ```

3. Go to the section that matches the largest directory.

## If logs are large (`/var/log/postgresql`)

1. Delete only old rotated logs, for example `*.gz` files, after you confirm the retention policy.
2. Do not delete the log file that PostgreSQL currently writes.
3. Check that log rotation runs. Assumption: the host uses `logrotate`.

## If `pg_wal` is large

Do not remove files. Find out why PostgreSQL keeps the WAL, and fix that cause. PostgreSQL will then remove old WAL files by itself.

1. Check for an unused replication slot.
   ```sql
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```
2. Check if WAL archiving fails.
   ```sql
   SELECT failed_count, last_failed_time FROM pg_stat_archiver;
   ```
3. Check if a replica is behind.
   ```sql
   SELECT client_addr, state, replay_lag FROM pg_stat_replication;
   ```
4. Fix the cause that you found:
   - Archiving fails: repair the `archive_command` target, for example a full or unreachable destination.
   - Replica is behind or down: restore the replica so it can catch up.
   - Slot is inactive: confirm that no consumer needs it. Then drop it.
     ```sql
     SELECT pg_drop_replication_slot('slot_name');
     ```
     A dropped slot can force a full rebuild of its replica. Ask the replica owner first.
5. Wait for the next checkpoint, or run `CHECKPOINT;`. Disk usage in `pg_wal` will then fall.

## If the data directory is large (`/var/lib/postgresql`, outside `pg_wal`)

1. Find the largest tables.
   ```sql
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. Remove old data or archive it, with the data owner's approval.
3. Use `VACUUM FULL` only as a last step. It locks the table and needs free space equal to the table size.

## If you cannot free space

1. Expand the volume or add disk.
2. Escalate to the database on-call. Do this at once if usage nears 100%, because PostgreSQL stops when the disk is full.

## Verify

1. Run `df -h` again. Usage must be below 90%.
2. Make sure that replication and archiving work (see the `pg_wal` queries).
3. Record the cause and the fix in the incident notes.
