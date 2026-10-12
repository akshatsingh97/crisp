Bottom line: Check the PostgreSQL version before you run the migration, because on version 10 or older it blocks all reads and writes on the orders table.

The migration adds a NOT NULL column with a default value to the orders table. The table has about 120 million rows.

On PostgreSQL 11 and later, adding a column with a constant default is a metadata-only change. It is nearly instant.

On PostgreSQL 10 or older, the migration rewrites the entire table. It holds an ACCESS EXCLUSIVE lock for the whole time. This blocks all reads and writes.

If the ALTER TABLE queues behind long-running queries, it also blocks every query that arrives after it. A short lock_timeout makes the ALTER TABLE give up instead.

Before you run the migration in production:

1. Take a full backup.
2. Restore the backup to test it. A backup that was never tested might not work when you need it.
3. Check the server version with `SELECT version()`.
4. Set lock_timeout to about 5 seconds.
5. Run the migration.

Terms:
- NOT NULL: the column must always have a value.
- Metadata-only change: the database edits the table definition and does not touch the rows.
- ACCESS EXCLUSIVE lock: the strongest table lock, which blocks all other access.
- lock_timeout: the longest time a statement waits for a lock before it fails.
- ALTER TABLE: the SQL command that changes a table definition.

Not clear in the original:
- "Basically instant" has no measured time.
- The text does not say what to do if the server runs version 10 or older.
- "Something like 5 seconds" is a suggestion, not a tested value.
