Here is the runbook. It starts with the rule on pg_wal, then goes from the quickest check to the deepest.

Do not delete files in pg_wal by hand. If you do, Postgres can fail to start, and the database can lose data. WAL (the write-ahead log, a record of every change) is removed by Postgres itself when it no longer needs a file.

Alert: disk usage over 90% on the database host.

1. Log in to the database host.
2. Run `df -h /var/lib/postgresql /var/log/postgresql` to see which disk is full.
3. Run `sudo du -sh /var/lib/postgresql/*/main/pg_wal /var/lib/postgresql/*/main/base /var/log/postgresql` to see which folder is largest. If your cluster is not named `main`, change the path.
4. If /var/log/postgresql is largest, list the old logs with `sudo find /var/log/postgresql -name '*.gz' -mtime +7`. Make sure that the list is correct, then add `-delete` to the command.
5. If pg_wal is largest, find out why Postgres keeps the files. Do not remove them. Go to step 6.
6. Run this query in `psql` to find a replication slot (a marker that holds WAL for a replica) that holds a lot of WAL:
```
SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained FROM pg_replication_slots;
```
7. If a slot is inactive and holds a lot of WAL, find its owner. If the owner confirms that the replica is gone, run `SELECT pg_drop_replication_slot('slot_name');`. If the replica is still in use, repair the replica so that it catches up.
8. Run `SELECT archived_count, failed_count, last_failed_wal, last_failed_time FROM pg_stat_archiver;` to check archiving. If `failed_count` grows, read the Postgres log, fix the cause of the `archive_command` failure, and wait.
9. After you fix the cause, run `CHECKPOINT;` in `psql`. Postgres then removes the WAL files that it no longer needs.
10. If /var/lib/postgresql/*/main/base is largest, run this query to find the biggest tables:
```
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
```
11. Do not run `VACUUM FULL` on a nearly full disk. It needs extra space to copy the table. Ask the table owner to archive old data, or add disk space.
12. Run `df -h` again. Make sure that usage is below 90% and that the alert clears.
13. If you cannot free enough space, extend the volume and tell the database team.
