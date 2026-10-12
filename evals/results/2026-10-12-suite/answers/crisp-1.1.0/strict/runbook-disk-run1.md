# Runbook: Disk usage over 90% on the database host

This runbook helps you free disk space safely. The alert fires when a disk passes 90% use.

## Rules

- Never delete, move, or edit files in `pg_wal` by hand. This can corrupt the database and make it unable to start.
- Never run `rm` in `/var/lib/postgresql`.

## Find the cause

1. Find the full disk.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Find the largest directory.
   ```
   du -sh /var/lib/postgresql/*/main/pg_wal /var/lib/postgresql /var/log/postgresql
   ```
   The path of `pg_wal` can differ on your host. This is an assumption.
3. If `pg_wal` is large, find the reason. The database keeps WAL files (write-ahead log) until nothing needs them.
4. Check for a replication slot that is not active. A stuck slot keeps WAL files forever.
   ```
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```
5. Check for archive failures. A failing archive command also keeps WAL files.
   ```
   SELECT last_archived_time, last_failed_time, failed_count FROM pg_stat_archiver;
   ```

## Fix the cause

If a slot is not active, find its owner first. Dropping a slot can break a replica that still needs it.

1. If a replica is down, restore it so that it reads the WAL and the slot moves forward.
2. If the replica is gone for good, drop the slot. Get approval from the database owner first.
   ```
   SELECT pg_drop_replication_slot('slot_name');
   ```
3. If archiving fails, read the error in the PostgreSQL log. Fix the archive target or command. The database then clears old WAL by itself.
4. Wait a few minutes. Run `df -h` again to confirm that usage falls.

## Free space from logs

If `/var/log/postgresql` is large, you can remove old logs. This is safe. Do not touch the log file that is open now.

1. Compress old log files.
   ```
   gzip /var/log/postgresql/<old-log-file>
   ```
2. If space is still short, copy the oldest logs to other storage. Then delete the originals.

## Escalate

Escalate to the database owner if any of these is true:

- Usage stays over 90% after the steps above.
- Usage rises fast and the disk will fill within the hour.
- The cause is in `/var/lib/postgresql` data files, not in WAL or logs.

The long-term fix is to add disk space or to enable log rotation. Make sure that someone owns this action.
