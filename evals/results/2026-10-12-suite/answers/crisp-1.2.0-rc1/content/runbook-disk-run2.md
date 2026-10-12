# Runbook: disk usage over 90% on the database host

This runbook helps you find what fills the disk and free space safely. Paths are `/var/lib/postgresql` (data), `pg_wal` (WAL, write-ahead log files), and `/var/log/postgresql` (logs).

## Warning

Never delete, move, or edit files in `pg_wal` by hand. This can corrupt the database and stop it from starting. Let PostgreSQL remove WAL files itself.

## 1. Confirm the alert

1. Run `df -h /var/lib/postgresql /var/log/postgresql`.
2. Note which filesystem is above 90%. If both paths share one filesystem, treat them together.

## 2. Find what uses the space

1. Run `du -xh --max-depth=1 /var/lib/postgresql | sort -h`.
2. Run `du -sh /var/lib/postgresql/*/main/pg_wal`. This path is an assumption. Adjust it to your version and layout.
3. Run `du -sh /var/log/postgresql`.
4. Go to the section that matches the largest consumer.

## 3A. Logs are large

1. List files with `ls -lh /var/log/postgresql`.
2. Compress or remove old rotated logs. Copy them elsewhere first if you need them for audits.
3. Check that log rotation runs. If it does not, fix the rotation setup.
4. Do not delete the log file that PostgreSQL currently writes to.

## 3B. pg_wal is large

PostgreSQL keeps WAL files while something still needs them. Find that cause. Do not remove the files.

1. Check replication slots (named markers that hold WAL for a consumer):
   ```sql
   SELECT slot_name, active,
          pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
   FROM pg_replication_slots;
   ```
2. Check archiving:
   ```sql
   SELECT last_archived_wal, last_failed_wal, last_failed_time FROM pg_stat_archiver;
   ```
3. Check replica lag with `SELECT * FROM pg_stat_replication;`.
4. Fix the cause:
   - If archiving fails, repair `archive_command` or its target. Check the PostgreSQL log for the error.
   - If a replica is down or behind, restore it so it can catch up.
   - If a slot is inactive and nobody uses it, confirm with its owner. Then run `SELECT pg_drop_replication_slot('slot_name');`.
5. Warning: dropping a slot breaks the consumer that uses it. That consumer may need a full resync.
6. After the cause is fixed, PostgreSQL removes old WAL at the next checkpoint. You can run `CHECKPOINT;` to speed this up.
   Expected result: the `pg_wal` size shrinks.

## 3C. Data files are large

1. Find the biggest tables and indexes with `pg_total_relation_size`.
2. Remove data that the owning team confirms is not needed.
3. Warning: plain `VACUUM` does not return space to the operating system. `VACUUM FULL` does, but it locks the table. It also needs free space for a full copy of the table. Do not run it on a nearly full disk.

## 4. If you cannot free enough space

1. Extend the volume or add disk.
2. Escalate to the database owner or on-call lead if the disk is above 95% and still growing. The database stops writing when the disk is full.

## 5. Verify

1. Run `df -h` and confirm usage is below 90%.
2. Confirm `pg_wal` is not growing. Check again after 10 minutes.
3. Confirm the alert clears.
4. Record the cause and the fix in the incident notes.
