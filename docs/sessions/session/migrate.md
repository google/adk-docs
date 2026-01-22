# Session database schema migration

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.0</span>
</div>

If you are using `DatabaseSessionService` and upgrading to ADK Python release
v1.22.0 or higher, you must also migrate your database to the new schema. Starting
with ADK Python release v1.22.0, the database schema for
`DatabaseSessionService` has been updated from `v0`, which is a pickle-based
serialization, to `v1`, which uses JSON-based serialization.

!!! warning "Warning: Breaking change"

    The schema change from `v0` pickle format to `v1` JSON format is a breaking
    change. You must migrate your existing database to continue using
    `DatabaseSessionService` with ADK Python v1.22.0 and higher.

## Migrate session database

A migration script is provided to facilitate the migration process. The script
reads data from your existing database, converts it to the new format, and
writes it to a new database. You can run the migration using the ADK Command
Line Interface (CLI) `migrate session` command, as shown in the following examples:

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

For detailed information on migrating between session databases versions, see the
[Sessions Migration README](https://github.com/google/adk-python/blob/main/src/google/adk/sessions/migration/README.md).