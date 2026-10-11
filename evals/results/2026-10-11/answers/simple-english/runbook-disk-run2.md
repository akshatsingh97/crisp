Here is the runbook. Never delete files in pg_wal by hand. Postgres removes them itself, and a wrong delete can corrupt the database or stop it from starting.

Alert: disk usage over 90% on the database host

1. Find out which location is full.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   sudo du -sh /var/lib/postgresql/*/*/pg_wal /var/log/postgresql
   ```

2. If /var/log/postgresql is large, rotate the logs and remove old compressed logs.
   ```
   sudo logrotate -f /etc/logrotate.d/postgresql-common
   sudo find /var/log/postgresql -name '*.gz' -mtime +14 -delete
   ```

3. If pg_wal is large, find out why Postgres keeps the WAL files. WAL (write-ahead log) is the change record that Postgres writes first. Postgres keeps these files for two main reasons. A replication slot (a marker that holds WAL for another server) can be stuck. WAL archiving can also be failing.

4. Look at the replication slots.
   ```
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```
   If a slot shows `active = f`, ask the slot owner whether the slot is still needed. If the owner says no, drop the slot. Postgres then removes the old WAL files by itself.
   ```
   SELECT pg_drop_replication_slot('slot_name');
   ```

5. Look at WAL archiving.
   ```
   SELECT archived_count, failed_count, last_failed_wal, last_failed_time FROM pg_stat_archiver;
   ```
   If `last_failed_time` is recent, fix the archive target. For example, free space on the archive disk or restore network access to it. Postgres then clears the WAL backlog by itself.

6. If the data in /var/lib/postgresql is large, find the biggest tables.
   ```
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
   Give the list to the table owners so that they can archive or remove old data. Do not run `VACUUM FULL` on a nearly full disk, because it needs extra space to work.

7. If usage stays over 90% after these steps, add disk space or escalate to the database owner.

8. Run `df -h` again and make sure that usage is below 90% before you close the alert.
