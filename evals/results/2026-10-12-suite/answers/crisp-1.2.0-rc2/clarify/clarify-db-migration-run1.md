Bottom line: Before you run the migration, take a restore-tested backup, check that the server is PostgreSQL 11 or later, and set `lock_timeout`.

The migration adds a NOT NULL column with a default value to the `orders` table, which has about 120 million rows.

1. Take a full backup of production.
2. Restore the backup to verify it works. A backup that you never tested can fail when you need it.
3. Run `SELECT version();` to check the server version. The result decides how risky the migration is.
4. Set `lock_timeout` to about 5 seconds before the `ALTER TABLE`.

What the version means:

- PostgreSQL 11 and later: adding a column with a constant default is a metadata-only change. It is nearly instant.
- PostgreSQL 10 or older: the server rewrites the entire table. It holds an ACCESS EXCLUSIVE lock for the whole rewrite. This blocks all reads and writes on a table with 120 million rows.

Why you need `lock_timeout`: without it, the `ALTER TABLE` waits behind long-running queries. Everything else then waits behind the `ALTER TABLE`. With a 5-second `lock_timeout`, the `ALTER TABLE` gives up instead of blocking other queries.

Terms:
- Metadata-only change: the server changes the table definition and does not rewrite any rows.
- ACCESS EXCLUSIVE lock: the strongest table lock. No other session can read or write the table.
- `lock_timeout`: a setting for how long a statement waits for a lock before it fails.
- Table rewrite: the server copies every row into a new table file.

Not clear in the original:
- "Basically instant" has no measured time.
- The text does not say how to verify the restore.
- The text does not define "long-running queries".
- The 5-second value is only an example ("something like").
