# Runbook: Disk usage over 90% on the database host

**Rule: never delete files in `pg_wal` by hand.** Removing WAL files can corrupt the database or break replication and recovery. Free WAL space only by fixing why Postgres is keeping it (see step 3).

## 1. Triage (about 5 minutes)
Find out what is using the space:
```bash
df -h /var/lib/postgresql /var/log/postgresql
du -xsh /var/lib/postgresql/*/main/pg_wal /var/lib/postgresql/*/main/base /var/log/postgresql
```
The path of the data directory depends on your version and layout, so adjust the globs to match. Then go to the section for the biggest consumer.

## 2. Logs are large (`/var/log/postgresql`)
This is the safest place to free space.
1. Compress or delete old, rotated logs: `gzip` the old files or `rm` the ones that are already rotated. Do not touch the current log file.
2. If the current log is huge, force a rotation with `SELECT pg_rotate_logfile();` and then handle the old file.
3. Find out why it grew. Likely causes are `log_min_duration_statement` set too low, an error loop, or `log_statement = 'all'`.
4. Check that logrotate is running.

## 3. `pg_wal` is large
WAL is only recycled once Postgres no longer needs it. Find out what is holding it:
```sql
-- Replication slots (the most common cause)
SELECT slot_name, active, restart_lsn,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
FROM pg_replication_slots ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- Archiving failures
SELECT archived_count, failed_count, last_failed_wal, last_failed_time FROM pg_stat_archiver;

-- Replica lag
SELECT client_addr, state, replay_lag FROM pg_stat_replication;
```
| Cause | Fix |
|---|---|
| Inactive or stuck replication slot | Bring the consumer back. If it is permanently gone, drop the slot with `SELECT pg_drop_replication_slot('name');`. Confirm with the owner first. |
| `archive_command` failing | Fix the cause (full or unreachable archive target, permissions). Postgres then archives and recycles the WAL itself. |
| Replica far behind | Fix the replica or the network. |
| Long-running transactions or heavy write burst | Find them in `pg_stat_activity`. Then run `CHECKPOINT;` and check `max_wal_size`. |

After the cause is fixed, Postgres cleans up `pg_wal` on its own. Check again after a checkpoint.

## 4. Data is large (`base`)
- Look for the largest tables and indexes, and for bloat. Run `VACUUM` as needed.
- Remove temp files, old dumps and backups that are stored on this volume.
- Drop unused data only with the data owner's approval.

## 5. If it is still not enough
- **Short term:** extend the volume or add disk. This is often the quickest safe option.
- **Escalate** to the DBA on-call if usage is above 95% or still climbing. A full disk makes Postgres stop accepting writes.

## 6. After the incident
- Record the cause and what you did.
- Add or tune alerts on `pg_wal` size, replication slot lag, and archive failures.
- Review log rotation and retention, plus capacity planning.
