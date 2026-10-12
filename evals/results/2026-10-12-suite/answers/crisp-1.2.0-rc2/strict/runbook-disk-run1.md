# Runbook: disk usage over 90% on the database host

**Rule: never delete or move files in `pg_wal` by hand.** This can corrupt the database and make recovery impossible. Postgres removes old WAL (write-ahead log) files itself once nothing needs them.

Assumption: the WAL path is `/var/lib/postgresql/<version>/<cluster>/pg_wal`.

## Steps

1. Find the full filesystem.
   ```
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Find the largest directories.
   ```
   du -sh /var/lib/postgresql/*/*/pg_wal /var/lib/postgresql/*/*/base /var/log/postgresql
   ```
3. If logs are large, free space there first. Old rotated logs are safe to compress or delete. Run `logrotate` if rotation has stopped.
4. If `pg_wal` is large, find out why Postgres keeps WAL. Run each query and read the result.
   ```
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   SELECT * FROM pg_stat_replication;
   SELECT last_archived_time, last_failed_time, failed_count FROM pg_stat_archiver;
   ```
5. Fix the cause that you find:
   - An inactive slot holds WAL. Bring the consumer back online.
   - A replica is far behind. Fix the replica or the network.
   - `failed_count` is rising. Fix the `archive_command` or the archive target.
6. If the database host is not the only copy of the data, ask the owner before you drop a stuck slot. The warning comes first. Dropping a slot breaks its consumer, and a replica will need a rebuild.
   ```
   SELECT pg_drop_replication_slot('slot_name');
   ```
7. After the fix, run `CHECKPOINT;` and watch `pg_wal` shrink over the next minutes. If it does not shrink, an open slot or a failing archive still holds WAL.
8. If the data directory itself is large, find the big tables and plan cleanup or a larger disk.
   ```
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```

## Risks

- `VACUUM FULL` locks the table and needs free space equal to the table size. Do not run it on a nearly full disk.
- If the disk reaches 100%, Postgres will stop and refuse writes. If usage passes 95% and you cannot free space, extend the volume now.

## Escalate

Page the database owner if usage stays over 90% after step 7, or if you cannot find the cause.
