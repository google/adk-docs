# Session database schema migration

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.1</span>
</div>

If you are using `DatabaseSessionService` and upgrading to ADK Python release
v1.22.0 or higher, you should migrate your database to the new session database
schema. Starting with ADK Python release v1.22.0, the database schema for
`DatabaseSessionService` has been updated from `v0`, which is a pickle-based
serialization, to `v1`, which uses JSON-based serialization. Previous `v0` session
schema databases will continue to work with ADK Python v1.22.0 and higher versions,
but the `v1` schema may be required in future releases.

If you use ADK Go, see [Schema updates in ADK Go](#schema-updates-in-adk-go)
instead. The migration command on this page does not apply to ADK Go databases.

## Migrate session database

A migration script is provided to facilitate the migration process. The script
reads data from your existing database, converts it to the new format, and
writes it to a new database. You can run the migration using the ADK Command
Line Interface (CLI) `migrate session` command, as shown in the following examples:

!!! warning "Required: ADK Python v1.22.1 or higher"

    ADK Python v1.22.1 is required for this procedure because it includes the
    migration command line interface function and bug fixes to support the session
    database schema change.

=== "SQLite"

    ```bash
    adk migrate session \
      --source_db_url=sqlite:///source.db \
      --dest_db_url=sqlite:///dest.db
    ```

=== "PostgreSQL"

    ```bash
    adk migrate session \
      --source_db_url=postgresql://localhost:5432/v0 \
      --dest_db_url=postgresql://localhost:5432/v1
    ```

After running the migration, update your `DatabaseSessionService` configuration
to use the new database URL you specified for `dest_db_url`.

## Schema updates in ADK Go

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-go">Go v0.1.0</span>
</div>

ADK Go has no `v0` to `v1` migration. Do not run `adk migrate session` on a
database created by ADK Go. The command expects the ADK Python `v0` format,
which stores event actions with pickle, while ADK Go stores them as JSON. On a
SQLite database created by ADK Go the command fails, and where it does run, it
replaces every event's actions with empty ones.

The ADK Go session service updates its schema in place instead, through
`database.AutoMigrate`. Call it every time your application starts, before it
serves traffic:

```go
if err := database.AutoMigrate(sessionService); err != nil {
    log.Fatal(err)
}
```

`AutoMigrate` creates missing tables and columns, and it never drops a column.
It also changes the type, size, or nullability of an existing column when that
differs from what ADK Go expects. You can run it repeatedly.

!!! warning "Managing the schema yourself"

    If you create and alter the session tables yourself instead of running
    `AutoMigrate`, add any new columns before you deploy the ADK Go release that
    introduces them. Until they exist, every write to that table fails, including
    writes that do not use the new columns.
