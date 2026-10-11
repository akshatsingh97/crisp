# Runbook: disk usage over 90% on the database host

Free space by removing old logs or fixing the cause of WAL growth. Never delete files in `pg_wal` by hand.

## Warning

Do not delete, move, or edit any file in `pg_wal`. Postgres needs these files for crash recovery and replication. Manual removal can corrupt the database. Postgres removes old WAL by itself once nothing needs it.

## Triage

1. Run `df -h /var/lib/postgresql /var/log/postgresql`. The output shows which filesystem is over 90%.
2. Run `sudo du -xh --max-depth=2 /var/lib/postgresql | sort -h | tail -n 15`. The output shows whether `pg_wal` or the table data is largest.
3. Run `sudo du -sh /var/log/postgresql`. Compare the size with the other two.

## Case A: logs are large

1. Run `ls -lhS /var/log/postgresql`. The largest files appear first.
2. Compress old rotated logs with `gzip`.
3. Delete old logs only if your retention policy allows it. Do not delete the log file Postgres is writing now.
4. Check that log rotation runs. Fix it if it does not.

## Case B: `pg_wal` is large

`pg_wal` grows when something blocks WAL removal. Common causes are an unused replication slot, a failing archive command, or a lagging replica.

1. Run `SELECT slot_name, active, restart_lsn FROM pg_replication_slots;`. An inactive slot with an old `restart_lsn` holds WAL.
2. Run `SELECT * FROM pg_stat_archiver;`. A recent `last_failed_time` means archiving fails. Fix the archive target or command.
3. Run `SELECT * FROM pg_stat_replication;`. If a replica lags, restore its connection or speed.

Dropping a slot breaks the replica or tool that uses it. Confirm with the slot owner that it is abandoned. Then run:

4. `SELECT pg_drop_replication_slot('slot_name');`
5. Wait for the next checkpoint. Postgres then removes the old WAL itself. Run `df -h` again to confirm usage falls.

## Case C: table data is large

1. Find the largest tables and check them for bloat (dead rows that waste space).
2. Do not run `VACUUM FULL` on a nearly full disk. It needs extra space to rewrite the table.
3. Ask for a larger volume. Expanding the disk is the safe fix.

## Escalate

If usage is above 95% and still rising, page the database owner now. If the WAL disk fills completely, Postgres can stop and refuse to start.

Assumptions: you have `psql` superuser access and `sudo` on the host. The data directory path may include a version number, such as `/var/lib/postgresql/16/main/pg_wal`.
