# Runbook: disk usage over 90% on the database host

This runbook helps you find what fills the disk and free space safely. It assumes PostgreSQL runs on Linux and you have shell access and a database superuser.

## Rule for pg_wal

Never delete, move, or edit files in `pg_wal` by hand. PostgreSQL needs them for crash recovery and replication. Manual deletion can corrupt the database. PostgreSQL removes old WAL files itself once nothing needs them.

## Steps

1. Confirm the alert and see which filesystem is full.

   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```

2. Find the largest directories.

   ```
   du -sh /var/lib/postgresql/*/* /var/log/postgresql
   ```

   Use `du` only to read sizes. Do not remove anything in this step.

### If /var/log/postgresql is large

3. Delete old rotated log files that your retention policy no longer needs.
4. Check that log rotation works. If it does not, fix the rotation setup and escalate the root cause.

### If pg_wal is large

WAL files pile up when something blocks their removal. Check the two common causes. Read the output only.

5. Check for a stuck replication slot (a marker that makes the server keep WAL for a consumer).

   ```sql
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```

   A slot with `active = f` and an old `restart_lsn` holds WAL.

6. Check for a failing archive command.

   ```sql
   SELECT last_failed_wal, last_failed_time FROM pg_stat_archiver;
   ```

   If `last_failed_time` is recent, fix the archive destination or command.
7. If a replica is down or lagging, restore the replica.

   Do not drop a replication slot until its owner confirms that the consumer is gone. A dropped slot can force a full replica rebuild. If the owner confirms, run this:

   ```sql
   SELECT pg_drop_replication_slot('slot_name');
   ```

8. Wait for the next checkpoint (a point where PostgreSQL flushes data to disk). PostgreSQL then removes the freed WAL files. Run `df -h` again to confirm usage drops.

### If the table data is large

9. Find the largest tables and decide with the data owner what to archive or remove.
10. If the growth is real, add disk space.

## Escalate

If usage stays above 90% after these steps, page the on-call DBA. If the disk reaches 100%, escalate at once. PostgreSQL will stop accepting writes.
