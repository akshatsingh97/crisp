# Runbook: Disk usage over 90% on the database host

Use this runbook when the disk that holds `/var/lib/postgresql` passes 90%. Act fast, because PostgreSQL stops accepting writes when the disk is full.

## Rule

Never delete, move, or edit files in `pg_wal` by hand. This can corrupt the database and lose data. PostgreSQL removes old WAL (write-ahead log) files itself once the cause of the growth is fixed.

## Steps

1. Confirm the alert and check whether data and logs share one filesystem.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Find the largest directory. Expect one of `pg_wal`, table data (`base`), or `/var/log/postgresql`.
   ```
   sudo du -xh --max-depth=2 /var/lib/postgresql /var/log/postgresql | sort -rh | head -20
   ```
3. Go to the section that matches the result.

## If logs are large

1. Rotate the logs.
   ```
   sudo logrotate -f /etc/logrotate.d/postgresql-common
   ```
   This path is an assumption. Use your own logrotate config if it differs.
2. Delete old rotated or compressed logs in `/var/log/postgresql` only if your retention policy allows it. Never delete the active log file.
3. Read the newest log to find why it grew. Common causes are repeated errors or very verbose query logging.

## If pg_wal is large

WAL grows when something still needs it. Check these causes in order.

1. Check for inactive replication slots. A slot with `active = f` and a large `retained` value is the likely cause.
   ```
   SELECT slot_name, active,
          pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
   FROM pg_replication_slots;
   ```
2. Check for WAL archive failures. A rising `failed_count` means the archive target is broken.
   ```
   SELECT archived_count, failed_count, last_failed_wal, last_failed_time
   FROM pg_stat_archiver;
   ```
3. Fix the cause.
   - Archive failing: repair the archive target, such as space, credentials, or network. WAL clears by itself after archiving resumes.
   - Replica lagging or down: restore the replica so it catches up.
   - Slot abandoned: confirm with its owner that nobody needs it. Then drop it. This breaks that consumer, which then needs a rebuild.
     ```
     SELECT pg_drop_replication_slot('slot_name');
     ```
4. Wait a few minutes and run `df -h` again. Space returns after the next checkpoint (a periodic flush of data to disk).

## If table data is large

1. Find the biggest tables.
   ```
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class WHERE relkind = 'r'
   ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. Ask the data owner before you drop or archive any data.
3. Do not run `VACUUM FULL` on a nearly full disk. It locks the table and needs extra free space for a copy. Plain `VACUUM` frees space for reuse inside PostgreSQL but does not shrink files.

## If you cannot free space quickly

Extend the volume or add disk, then escalate to the database on-call. Do this before the disk reaches 100%.

## Verify

1. Confirm `df -h` shows usage below 90% and not still rising.
2. Confirm the alert clears.
3. Record the root cause and the fix in the incident notes.
