Bottom line: Before the production migration, take and test a full backup, check that PostgreSQL is version 11 or later, and set `lock_timeout` to about 5 seconds.

**Why the version matters**

The migration adds a NOT NULL column with a default value to the `orders` table. That table has about 120 million rows.

- On PostgreSQL 11 and later, a constant default is a metadata-only change. It is nearly instant.
- On PostgreSQL 10 or older, the database rewrites the entire table. It holds an ACCESS EXCLUSIVE lock the whole time. That lock blocks all reads and writes.

**Steps**

1. Take a full backup.
2. Restore the backup to check that it works. A backup that was never tested can fail when you need it.
3. Check the server version with `SELECT version()`. If the version is 10 or older, the migration will lock `orders` for the whole rewrite.
4. Set `lock_timeout` to about 5 seconds. Then the `ALTER TABLE` gives up instead of waiting behind long-running queries. Without a timeout, the waiting `ALTER TABLE` blocks every query queued behind it.

Terms:
- Metadata-only change: the database edits the table definition and does not touch the stored rows.
- ACCESS EXCLUSIVE lock: the strictest table lock. No other session can read or write the table.
- Constant default: a fixed default value, not one computed per row.
- `lock_timeout`: a setting that cancels a statement if it waits too long for a lock.

Not clear in the original:
- "Basically instant" has no measured time.
- The text does not say what to do if the server runs PostgreSQL 10 or older.
- The 5 second value is only an example ("something like"). The text gives no reason for it.
