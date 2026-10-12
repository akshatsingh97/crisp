# Runbook: disk usage over 90% on the database host

Assumptions: you have sudo access and a PostgreSQL superuser in psql. The commands below are standard PostgreSQL and Linux commands.

## Rule

Never delete files in `pg_wal` by hand. A wrong delete can corrupt the database and stop it from starting. PostgreSQL removes old WAL (write-ahead log) files by itself when nothing needs them. To free WAL space, remove the cause of the retention.

## Steps

1. Find which path is full.
   ```
   df -h
   sudo du -sh /var/lib/postgresql/* /var/log/postgresql
   sudo du -sh /var/lib/postgresql/*/*/pg_wal
   ```
   The `pg_wal` path assumes the Debian layout. Adjust it if your layout differs.
2. Go to the section that matches the largest path.

## If /var/log/postgresql is large

Do not delete the log file that PostgreSQL has open now. Only touch old rotated files.

1. List the files by age: `ls -lht /var/log/postgresql`.
2. Compress old files: `sudo gzip <old-log-file>`.
3. If space is still short, copy old logs to other storage, then delete them from the host.
4. Make sure that log rotation works. Check `logrotate` or the `log_rotation_age` and `log_rotation_size` settings.

## If pg_wal is large

Find the cause with these three queries. The most common causes are an unused replication slot, a failing archive command, and a lagging replica.

1. Check replication slots. A slot with `active = f` and a large `retained` value holds WAL.
   ```sql
   SELECT slot_name, active,
          pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
   FROM pg_replication_slots;
   ```
2. Check archiving. A rising `failed_count` means WAL waits for a successful archive.
   ```sql
   SELECT archived_count, failed_count, last_failed_wal, last_failed_time
   FROM pg_stat_archiver;
   ```
3. Check replicas. A replica with high lag holds WAL for itself.
   ```sql
   SELECT client_addr, state, replay_lag FROM pg_stat_replication;
   ```

Then apply the fix that matches.

- Inactive slot with a consumer that will return: restart the consumer. WAL frees after it catches up.
- Inactive slot with a consumer that is gone for good: confirm with the slot owner first. Then run `SELECT pg_drop_replication_slot('<slot_name>');`. The consumer must resync from scratch.
- Failing archive: read the PostgreSQL log for the `archive_command` error. Fix the cause, for example a full or unreachable archive target or bad permissions. WAL frees after archiving succeeds.
- Lagging replica: restore its network or fix its replay. WAL frees after it catches up.

After the fix, WAL shrinks at the next checkpoints. To speed this up, run `CHECKPOINT;` as a superuser.

## If the data directory is large

1. Find the biggest tables: `SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;`
2. Run a plain `VACUUM` on bloated tables.
3. Do not run `VACUUM FULL` on a nearly full disk. It needs extra free space equal to the table size and takes an exclusive lock.
4. If the data is real growth, not bloat, grow the volume or archive old data.

## If the disk is still above 95%

If the disk reaches 100%, PostgreSQL cannot write WAL. It will crash and may not restart. Grow the volume now and escalate to the database owner. Do not wait for the root cause.

## Verify

1. Run `df -h` and make sure usage is below the alert threshold.
2. Re-run the three WAL queries and make sure that no slot is inactive, `failed_count` stays flat, and replica lag is low.
3. Record the cause and the fix in the incident ticket.
