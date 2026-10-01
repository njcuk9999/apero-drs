---
card_label: Useful MySQL commands
card_icon: fa-solid fa-database
---

# Useful MySQL commands

These examples are read-only unless marked **destructive**. Replace database,
table, and column names with those from the APERO profile. Do not paste
credentials into shared terminals, tickets, shell history, or documentation.

## Connect

```bash
mysql --host=HOST --user=USERNAME --password DATABASE_NAME
```

`--password` prompts securely. Avoid putting a password directly in the
command line. APERO's database connection settings are in the profile's
`database.yaml`; use the configured database backend and account.

## Discover a schema

```sql
SHOW DATABASES;
USE DATABASE_NAME;
SHOW TABLES;
DESCRIBE TABLE_NAME;
SHOW CREATE TABLE TABLE_NAME\G
```

## Inspect rows

```sql
SELECT * FROM TABLE_NAME LIMIT 20;
SELECT COUNT(*) FROM TABLE_NAME;
SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE_NAME
  AND TABLE_NAME = 'TABLE_NAME'
ORDER BY ORDINAL_POSITION;
```

Filter by an exact key and limit the result before inspecting large tables:

```sql
SELECT *
FROM TABLE_NAME
WHERE KEYNAME = 'VALUE'
ORDER BY DATE_OBS DESC
LIMIT 50;
```

## Transactions and changes

Start with `SELECT` to confirm the rows and predicates. For manual edits,
review the proposed change with the database administrator and use a
transaction where supported:

```sql
START TRANSACTION;
UPDATE TABLE_NAME SET COLUMN_NAME = 'NEW_VALUE' WHERE KEYNAME = 'VALUE';
SELECT * FROM TABLE_NAME WHERE KEYNAME = 'VALUE';
ROLLBACK;
```

The example ends in `ROLLBACK` intentionally. Replace it with `COMMIT` only
after confirming the database, affected row count, and intended values.

Do not use direct SQL to make routine APERO calibration/telluric/index changes.
Use APERO's database tools so filesystem products and database rows stay
consistent. Never run `DELETE`, `DROP`, or broad `UPDATE` commands on a
production database without an approved maintenance procedure and backup.
