# Runbook: Disk usage over 90% on the database host

**Rule: never delete or move files in `pg_wal` by hand.** Removing a WAL file Postgres still needs can make the database unrecoverable or break replicas. Free WAL space only by fixing why Postgres is retaining it.

## 1. Triage (2 min)
```bash
df -h /var/lib/postgresql /var/log/postgresql
du -sh /var/lib/postgresql/*/main/pg_wal /var/log/postgresql
du -sh /var/lib/postgresql/*/main/base/* | sort -h | tail
```
Identify which one is growing: **logs**, **pg_wal**, or **table data** (`base/`). Then go to the matching section.

## 2a. Logs are large (`/var/log/postgresql`)
This is the safest fix.
- Delete or compress old rotated logs: `gzip` the `*.log.1`, `*.log.2` files, or remove the oldest ones.
- Don't `rm` the active log file, because Postgres keeps it open and the space isn't freed. Truncate it instead: `: > current.log`.
- Follow-up: check the logrotate config and whether `log_min_duration_statement` or `log_statement` is too verbose.

## 2b. `pg_wal` is large
WAL piles up when something stops it from being recycled. Check these in order:

1. **Failing archiving.**
   ```sql
   SELECT archived_count, failed_count, last_failed_wal, last_failed_time FROM pg_stat_archiver;
   ```
   If `failed_count` is rising, fix the `archive_command` target (full disk or bucket, permissions, network). WAL is recycled once archiving catches up.

2. **Inactive or lagging replication slots.**
   ```sql
   SELECT slot_name, active,
          pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
   FROM pg_replication_slots ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;
   ```
   - If the consumer is a replica or CDC job that is down, bring it back so it catches up.
   - If the consumer is permanently gone, drop the slot with `SELECT pg_drop_replication_slot('<name>');`. **Confirm with the slot's owner first.** Dropping a slot breaks that consumer.

3. **Lagging replicas.** Check `pg_stat_replication` for lag, and fix the replica or network.

4. **Settings.** Review `wal_keep_size`, `max_wal_size`, and `archive_mode`. After the cause is fixed, a manual `CHECKPOINT;` lets Postgres recycle old segments.

## 2c. Table data is large (`base/`)
- Find the biggest tables and indexes with `pg_total_relation_size`.
- Look for bloat. Plain `VACUUM` doesn't shrink files. `VACUUM FULL` and `pg_repack` do, but they need extra disk space and locks, so plan them.
- Look for long-running transactions or stale slots blocking vacuum (`pg_stat_activity`).
- Drop or archive unneeded data only with the data owner's approval.

## 3. If space is critically low (>95%)
- Do the log cleanup (2a) first, since it is instant and safe.
- Extend the volume or attach more disk if the platform allows it.
- If Postgres has already stopped because `pg_wal` filled the disk, **don't delete WAL**. Add disk space, restart, and let it recover.

## 4. Verify and close
- `df -h` is below 85%, and `pg_stat_archiver` and `pg_replication_slots` look healthy.
- Note the root cause. Add or tune monitoring for archive failures, slot lag, and log rotation.

## Escalate to the DBA or on-call lead if
- A slot's owner is unknown.
- Archiving can't be fixed quickly.
- The database is down or won't start.
- Disk is still above 95% after the safe steps.
