# Runbook: Disk usage over 90% on the database host

**Warning:** Never delete, move, or edit files in `pg_wal` by hand. This can corrupt the database and stop it from starting. Fix the cause and let PostgreSQL remove old WAL itself.

## 1. Find what uses the space

```bash
df -h /var/lib/postgresql /var/log/postgresql
sudo du -xh --max-depth=1 /var/lib/postgresql/*/main | sort -h
sudo du -sh /var/log/postgresql
```

Go to the section that matches the largest directory.

## 2. Logs are large (`/var/log/postgresql`)

1. Force a rotation: `sudo logrotate -f /etc/logrotate.d/postgresql-common`
2. Delete old rotated or compressed logs that you no longer need.
3. Keep the current log file.
4. Find out why the logs grew, for example an error loop or `log_statement = all`.

## 3. `pg_wal` is large

Find out why PostgreSQL keeps the WAL. Run these in `psql`:

```sql
-- Inactive slots hold WAL
SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
-- Archive failures hold WAL
SELECT failed_count, last_failed_wal, last_failed_time FROM pg_stat_archiver;
-- Lagging replicas hold WAL
SELECT application_name, state, replay_lag FROM pg_stat_replication;
```

| Cause | Action |
|---|---|
| Archive command fails | Fix the command or the archive target, then check that `failed_count` stops rising. |
| Inactive slot | Restart the replica or consumer. If the slot is abandoned, confirm with its owner, then run `SELECT pg_drop_replication_slot('name');`. |
| Replica far behind | Fix the network or replica load, or rebuild the replica. |

After the fix, run `CHECKPOINT;`. PostgreSQL then removes the WAL it no longer needs. This can take a few minutes.

## 4. Data is large (`/var/lib/postgresql`, not `pg_wal`)

1. Find the largest tables: `SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) FROM pg_class ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;`
2. Remove data only with approval from the data owner.
3. Run a normal `VACUUM` to reuse dead space. Do not run `VACUUM FULL` on a nearly full disk, because it needs extra space.

## 5. If the cause is not fixable now

Extend the volume or add disk space. This is the safe way to gain time.

## Verify

- `df -h` shows usage under 80%.
- `pg_wal` shrinks after a checkpoint.
- The alert clears.

## Escalate

Page the DBA on call if any of these is true:
- Usage is over 95%.
- PostgreSQL logs `No space left on device` or `PANIC`.
- You cannot find the cause within 15 minutes.
