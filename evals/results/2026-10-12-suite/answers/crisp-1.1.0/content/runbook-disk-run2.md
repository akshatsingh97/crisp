# Runbook: Disk usage over 90% on the database host

**Rule:** Never delete, move, or edit files in `pg_wal` by hand. This can corrupt the database and stop it from starting. PostgreSQL removes old WAL (write-ahead log) files itself once nothing needs them.

## 1. Find what is using the space

1. Check the filesystem.

   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```

   Result: the use percentage for each path.

2. Find the largest directories.

   ```
   sudo du -xh --max-depth=3 /var/lib/postgresql | sort -h | tail -20
   ```

   Result: the largest directories, with the biggest last. Look for `pg_wal`.

3. Check the log directory.

   ```
   ls -lh /var/log/postgresql
   ```

## 2. If logs use the space

Do not delete the active log file. Delete only old rotated logs.

1. Compress or delete rotated logs that are past your retention period.
2. Run `df -h /var/log/postgresql` to confirm that usage dropped.

## 3. If `pg_wal` uses the space

WAL grows when archiving fails, a replica falls behind, or an unused replication slot holds it back.

1. Check for archiving failures.

   ```
   psql -c "SELECT * FROM pg_stat_archiver;"
   ```

   Result: a high `failed_count` or a recent `last_failed_time` means archiving is broken.

2. Check the replication slots.

   ```
   psql -c "SELECT slot_name, active, restart_lsn FROM pg_replication_slots;"
   ```

   Result: an inactive slot with an old `restart_lsn` is holding WAL.

3. If archiving fails, fix the cause, such as a full archive target or a broken `archive_command`.
4. If a replica lags, restore its connection to the primary.

If a slot is abandoned, confirm with its owner first. Dropping it forces that replica to be rebuilt.

5. Drop the abandoned slot.

   ```
   psql -c "SELECT pg_drop_replication_slot('<slot_name>');"
   ```

   Result: PostgreSQL will remove the freed WAL files at the next checkpoint.

## 4. If table data uses the space

Do not run `VACUUM FULL` on a nearly full disk. It needs extra space to copy the table.

1. Find the largest tables and ask the data owner to archive or purge old rows.
2. If the data is legitimate, expand the volume.

## 5. Confirm and escalate

1. Run `df -h` and confirm that usage is below 90%.
2. Wait for the alert to clear.
3. If you cannot find the cause or free space, escalate to the database owner.

**Assumptions:** The commands assume `psql` access as a superuser and a standard PostgreSQL setup. Adjust the connection options and paths to match your host.
