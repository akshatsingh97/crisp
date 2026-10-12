Bottom line: Before you migrate, take and test a full backup, check that the server runs PostgreSQL 11 or later, and set lock_timeout to about 5 seconds.

The migration adds a NOT NULL column with a default value to the orders table. That table has about 120 million rows.

1. Take a full backup of the database.
2. Restore the backup to confirm that it works. A backup that you never tested can fail when you need it.
3. Check the server version:

   ```sql
   SELECT version();
   ```

   - PostgreSQL 11 or later: adding a column with a constant default changes only metadata. It is almost instant.
   - PostgreSQL 10 or older: the command rewrites the entire table. It holds an ACCESS EXCLUSIVE lock for the whole time. That lock blocks all reads and writes.

4. Set lock_timeout to about 5 seconds before you run the ALTER TABLE. The ALTER TABLE will then give up instead of waiting behind long-running queries. Without it, the waiting ALTER TABLE blocks every query that arrives after it.

Terms:
- Metadata-only change: PostgreSQL updates the table definition and does not touch the stored rows.
- ACCESS EXCLUSIVE lock: the strongest table lock. No other session can read or write the table.
- lock_timeout: a setting for how long a command waits for a lock before it fails.
- Table rewrite: PostgreSQL copies every row into a new table file.

Not clear in the original:
- "Basically instant" has no measured time.
- The original does not say how to verify the restore.
- "Something like 5 seconds" is an example value, not a tested one.
