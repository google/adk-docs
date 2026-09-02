from google.adk.sessions import DatabaseSessionService
# Example using a local SQLite file:
# Note: The implementation requires an async database driver.
# For SQLite, use 'sqlite+aiosqlite' instead of 'sqlite' to ensure async compatibility.
db_url = "sqlite+aiosqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)