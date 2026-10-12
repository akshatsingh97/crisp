# Runbook: disk usage over 90% on the database host

**Rule:** Never delete or move files in `pg_wal` by hand. This can corrupt the database and stop recovery. Free WAL space only by fixing the cause that keeps the WAL.

## Triage

1. Find the full filesystem.
   ```bash
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Find the largest directories.
   ```bash
   du -xh --max-depth=2 /var/lib/postgresql | sort -h | tail -15
   du -sh /var/log/postgresql
   ```
3. Go to the section that matches the largest consumer.

## If logs are the cause

1. Check that logrotate runs for `/var/log/postgresql`.
2. Delete or compress old rotated logs. Do not delete the log file that PostgreSQL is writing now.
3. If one log grows fast, read it for error loops or very verbose logging settings.

## If pg_wal is the cause

WAL (write-ahead log, the change journal) grows when something holds it back. Check these causes in order.

1. Check for failing archiving. A rising `failed_count` or a recent `last_failed_time` means `archive_command` fails.
   ```sql
   SELECT * FROM pg_stat_archiver;
   ```
2. Check replication slots. A slot with `active = f` and a large retained size holds WAL.
   ```sql
   SELECT slot_name, active,
          pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
   FROM pg_replication_slots;
   ```
3. Check for lagging replicas.
   ```sql
   SELECT application_name, state, replay_lag FROM pg_stat_replication;
   ```
4. Fix the cause. Repair the archive target, restore the replica, or let the replica catch up.
5. Only if the slot owner confirms it is abandoned, drop it. The consumer will need a full rebuild.
   ```sql
   SELECT pg_drop_replication_slot('slot_name');
   ```

PostgreSQL removes the unneeded WAL itself at the next checkpoint. Expect `pg_wal` to shrink after the cause is fixed.

## If table data is the cause

1. Find the largest tables.
   ```sql
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class WHERE relkind = 'r' ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. Remove data only with owner approval. Plain `VACUUM` does not return space to the operating system.
3. `VACUUM FULL` returns space but takes an exclusive lock and needs free disk for the table copy. Use it only in a maintenance window.
4. If the data is legitimate, grow the volume.

## Verify and escalate

1. Run `df -h` again and confirm usage is below 90%.
2. Confirm `pg_wal` is stable or shrinking and the alert clears.
3. If the disk reaches 100%, PostgreSQL will stop accepting writes. Escalate to the DBA on call at once and grow the volume first.

Assumption: the `pg_wal` directory sits inside the data directory under `/var/lib/postgresql`. Adjust paths if your layout differs.
