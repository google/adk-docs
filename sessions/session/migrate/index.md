# Session database schema migration

Supported in ADKPython v1.22.1

If you are using `DatabaseSessionService` and upgrading to ADK Python release v1.22.0 or higher, you should migrate your database to the new session database schema. Starting with ADK Python release v1.22.0, the database schema for `DatabaseSessionService` has been updated from `v0`, which is a pickle-based serialization, to `v1`, which uses JSON-based serialization. Previous `v0` session schema databases will continue to work with ADK Python v1.22.0 and higher versions, but the `v1` schema may be required in future releases.

## Migrate session database

A migration script is provided to facilitate the migration process. The script reads data from your existing database, converts it to the new format, and writes it to a new database. You can run the migration using the ADK Command Line Interface (CLI) `migrate session` command, as shown in the following examples:

Required: ADK Python v1.22.1 or higher

ADK Python v1.22.1 is required for this procedure because it includes the migration command line interface function and bug fixes to support the session database schema change.

```bash
adk migrate session \
  --source_db_url=sqlite:///source.db \
  --dest_db_url=sqlite:///dest.db
```

```bash
adk migrate session \
  --source_db_url=postgresql://localhost:5432/v0 \
  --dest_db_url=postgresql://localhost:5432/v1
```

After running the migration, update your `DatabaseSessionService` configuration to use the new database URL you specified for `dest_db_url`.
