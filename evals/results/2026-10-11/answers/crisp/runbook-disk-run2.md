# Runbook: disk usage over 90% on the database host

**Never delete files in `pg_wal` by hand.** PostgreSQL needs these WAL files (write-ahead log, the record of database changes) for crash recovery. A manual delete can corrupt the database. Fix the cause of the growth and PostgreSQL will remove old WAL itself.

## Triage

1. Check which filesystem is full.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Find the largest directories.
   ```
   sudo du -xh --max-depth=2 /var/lib/postgresql /var/log/postgresql | sort -h | tail -20
   ```
3. Go to the section that matches the largest directory.

## If `/var/log/postgresql` is large

Logs are safe to remove. WAL is not logs. Do not touch `pg_wal` here.

1. List the files by size.
   ```
   ls -lhS /var/log/postgresql
   ```
2. Compress or delete old rotated log files. Keep the current log file.
3. Check that log rotation is set up. This runbook assumes `logrotate` is in use.

## If `pg_wal` is large

WAL grows when something blocks its removal. The usual causes are a stale replication slot, a failing archive command, or a lagging standby.

1. Check replication slots in `psql`.
   ```sql
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```
2. Check WAL archiving.
   ```sql
   SELECT last_archived_time, last_failed_time, last_failed_wal FROM pg_stat_archiver;
   ```
3. Fix the cause. Repair the archive command, or restore the lagging standby.
4. If a slot is inactive and its consumer is gone, confirm with the slot owner first. Then drop it.
   ```sql
   SELECT pg_drop_replication_slot('slot_name');
   ```
5. Wait for the next checkpoint. Check that `pg_wal` shrinks.

## If the data directory is large

1. List the largest tables in `psql`.
   ```sql
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class WHERE relkind = 'r'
   ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. Ask the data owner if old data can be archived or purged.
3. If growth is expected, extend the disk.

## Close out

1. Run `df -h /var/lib/postgresql` and check that usage is below 90%.
2. Confirm the alert clears.
3. If usage keeps rising or you cannot free space, extend the volume and page the database owner.
