# Runbook: Disk usage over 90% on the database host

This runbook helps you find what fills the disk and free space safely. Never delete, move, or edit files in `pg_wal` by hand. PostgreSQL needs those files for crash recovery. Manual deletion can corrupt the database and stop it from starting. PostgreSQL removes old WAL (write-ahead log) files itself once the cause of the build-up is fixed.

Assumption: `pg_wal` sits inside the data directory under `/var/lib/postgresql`. Replace `<ver>/main` with your real path.

## 1. Find what uses the space

1. Check the filesystems.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Check the three main areas.
   ```
   du -sh /var/lib/postgresql/<ver>/main/pg_wal
   du -sh /var/lib/postgresql/<ver>/main/base
   du -sh /var/log/postgresql
   ```
3. Go to the section below for the largest area.

## 2. Logs are largest (`/var/log/postgresql`)

Logs are safe to remove after you keep what you need.

1. List files by size.
   ```
   ls -lhS /var/log/postgresql
   ```
2. Delete old rotated or compressed logs that are past your retention period.
3. Do not delete the log file that PostgreSQL is writing now. Rotate it with `logrotate` instead, if it is configured.
4. Find why the logs grew. Look for repeated errors or a very low `log_min_duration_statement`.

## 3. `pg_wal` is largest

WAL grows when something holds it back. Find the cause and fix that. Do not touch the files.

1. Check replication slots. A slot that is not active keeps WAL forever.
   ```sql
   SELECT slot_name, active,
          pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
   FROM pg_replication_slots;
   ```
2. Check WAL archiving. A rising `failed_count` means `archive_command` fails and WAL piles up.
   ```sql
   SELECT archived_count, failed_count, last_failed_wal, last_failed_time
   FROM pg_stat_archiver;
   ```
3. Check replicas for lag.
   ```sql
   SELECT client_addr, state, replay_lag FROM pg_stat_replication;
   ```
4. Fix the cause that you found:
   - Archive failing: repair the archive target or command. Read the PostgreSQL log for the error.
   - Replica down or behind: restore the replica so it catches up.
   - Slot inactive and its consumer is gone: get approval from the slot owner, then drop it. Dropping a slot breaks that consumer for good.
     ```sql
     SELECT pg_drop_replication_slot('slot_name');
     ```
5. Run `CHECKPOINT;` to help PostgreSQL recycle old WAL. Then recheck the size of `pg_wal`.

## 4. Data is largest (`base`)

1. Find the largest tables.
   ```sql
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class WHERE relkind = 'r'
   ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. If a table has heavy bloat, run `VACUUM` on it. Plain `VACUUM` is safe but returns little space to the disk.
3. Do not run `VACUUM FULL` on a disk that is nearly full. It locks the table and needs extra free space for a full copy.
4. Remove data only with approval from the data owner.

## 5. If you cannot free enough space

1. Extend the volume or add disk. This is the safest fast fix.
2. Page the database on-call engineer if usage passes 95%. At 100% PostgreSQL can stop and refuse writes.

## 6. Verify

1. Run `df -h` and confirm usage is below 90%.
2. Confirm the alert clears.
3. Confirm `failed_count` no longer rises and replicas show `streaming`.
4. Write a short note on the cause and add a fix to prevent it, such as a retention limit or a monitor on replication slots.
