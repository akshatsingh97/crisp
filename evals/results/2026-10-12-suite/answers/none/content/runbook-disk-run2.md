# Runbook: disk usage over 90% on the database host

**Goal:** free space safely before the disk fills. If the disk fills, PostgreSQL stops.

## Warnings

- **Never delete files in `/var/lib/postgresql/*/pg_wal` by hand.** PostgreSQL still needs some of them. A wrong delete can corrupt the database or break replicas and recovery.
- Do not delete anything in `/var/lib/postgresql` except through PostgreSQL commands.
- Old logs in `/var/log/postgresql` are safe to remove or compress.

## 1. Find what uses the space

1. Check the disk: `df -h /var/lib/postgresql /var/log/postgresql`
2. Compare the three areas:
   `du -sh /var/lib/postgresql/*/pg_wal /var/lib/postgresql/*/base /var/log/postgresql`
3. Go to the section below for the largest area.

## 2. If logs are large

1. List the biggest files: `ls -lhS /var/log/postgresql | head`
2. Compress or delete old rotated logs. Do not delete the file that PostgreSQL is writing now.
3. If the active log is huge, rotate it: `SELECT pg_rotate_logfile();`
4. Find the cause (for example, `log_statement = 'all'` or an error loop) and fix it.

## 3. If `pg_wal` is large

WAL grows when PostgreSQL cannot remove old files. Find out why. Do not remove the files yourself.

1. Check replication slots:
   `SELECT slot_name, active, restart_lsn FROM pg_replication_slots;`
   - An inactive slot holds WAL forever. If the replica is gone, drop the slot with `SELECT pg_drop_replication_slot('name');`. Confirm with the owner first, because the replica cannot resume after this.
   - If the replica is only down, restart it so it catches up.
2. Check archiving: `SELECT * FROM pg_stat_archiver;`
   - If `failed_count` grows, fix `archive_command` or the archive target. WAL stays on disk until archiving works.
3. Check for a long-running transaction or a lagging replica: `SELECT * FROM pg_stat_replication;`
4. After the cause is fixed, run `CHECKPOINT;`. PostgreSQL then removes old WAL by itself. Space may take a few minutes to return.

## 4. If `base` (table data) is large

1. Find the largest tables: `SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;`
2. Check for bloat. `VACUUM` makes space reusable inside the table but does not shrink the disk use. `VACUUM FULL` does shrink it, but it locks the table and needs free space to run.
3. If growth is real, add disk space or archive old data.

## 5. If you cannot free space fast

Extend the volume. This is safer than any manual deletion.

## 6. Verify and close

- `df -h` shows usage below 80%.
- `pg_stat_archiver` shows no new failures, and no slot is stuck.
- Write a note on the cause and add a lower-threshold alert (for example, 75%) if one does not exist.

## Escalate

Page the database owner if usage is above 95%, if PostgreSQL has stopped, or if you are not sure whether a slot can be dropped.
