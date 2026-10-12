# Runbook: Disk usage over 90% on the database host

**Rule: never delete or move files in `pg_wal` by hand.** Manual deletion can corrupt the database and make it unable to start. Free WAL space only by fixing the cause (step 4).

## Impact

If the disk fills, PostgreSQL cannot write WAL (write-ahead log) and will stop. Act before usage reaches 100%.

## Steps

### 1. Confirm the alert

1. Check the filesystem:
   ```bash
   df -h /var/lib/postgresql /var/log/postgresql
   ```
2. Note whether both paths share one filesystem. This is an assumption. The output will show it.

### 2. Find the largest consumer

1. Compare the three areas:
   ```bash
   du -sh /var/lib/postgresql/*/main/pg_wal /var/log/postgresql
   du -xh --max-depth=2 /var/lib/postgresql | sort -h | tail -20
   ```
   The path `*/main` is an assumption. Adjust it to your version and cluster name.
2. Go to step 3 if logs are largest. Go to step 4 if `pg_wal` is largest. Go to step 5 otherwise.

### 3. Logs in /var/log/postgresql

1. List files by size and age:
   ```bash
   ls -lhS /var/log/postgresql
   ```
2. Delete or compress old rotated logs only. Do not touch the current log file.
3. Check that log rotation works. Find out why logs grew, for example an error loop or verbose logging.

### 4. WAL growth in pg_wal

WAL stays on disk when something still needs it. The usual causes are an inactive replication slot, a failing archive command, or a lagging replica.

1. Check replication slots:
   ```sql
   SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
   ```
2. Check archiving:
   ```sql
   SELECT last_archived_wal, last_failed_wal, last_failed_time FROM pg_stat_archiver;
   ```
3. Check replicas:
   ```sql
   SELECT application_name, state, replay_lag FROM pg_stat_replication;
   ```
4. Fix the cause. Repair the archive command or reconnect the replica.
5. Drop a slot only if you confirm its consumer is gone for good. The consumer will need a full rebuild.
   ```sql
   SELECT pg_drop_replication_slot('slot_name');
   ```
6. Wait for PostgreSQL to remove old WAL itself. It does this at the next checkpoint. You can run `CHECKPOINT;` to speed this up.
7. Confirm that `pg_wal` shrinks.

### 5. Data growth in /var/lib/postgresql

1. Find the largest tables:
   ```sql
   SELECT relname, pg_size_pretty(pg_total_relation_size(oid))
   FROM pg_class WHERE relkind = 'r'
   ORDER BY pg_total_relation_size(oid) DESC LIMIT 10;
   ```
2. Check for bloat (dead rows that waste space) and for stalled autovacuum.
3. Avoid `VACUUM FULL` on a nearly full disk. It locks the table and needs extra free space to run.
4. If the growth is real, expand the disk or archive old data.

## Escalate

Page the database owner if any of these is true:
- Usage passes 95%.
- The cause is not clear after step 2.
- A replication slot drop is the only fix.

## After the incident

- Confirm usage is below 90% and stays there.
- Record the cause and the fix.
- Add an earlier alert, for example at 80%.
