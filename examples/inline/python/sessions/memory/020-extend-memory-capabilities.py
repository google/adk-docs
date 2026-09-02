import asyncio
from google.adk.memory import InMemoryMemoryService

# Assume my_memory_service is an instance of InMemoryMemoryService
# and my_latest_events is a list of new adk.Event objects from the latest turn.
my_latest_events = [...]

async def update_incremental_memory(my_memory_service, my_latest_events):
    # Example 1: Basic incremental update
    await my_memory_service.add_events_to_memory(
        app_name="my-app",
        user_id="my-user",
        events=my_latest_events,
        session_id="my-optional-session-id"
    )

    # Example 2: Incremental update with Custom Metadata
    await my_memory_service.add_events_to_memory(
        app_name="my-app",
        user_id="my-user",
        events=my_latest_events,
        session_id="my-optional-session-id",
        custom_metadata={
            "my_custom_key": "my_custom_value"
        }
    )

async def update_session_memory(my_memory_service, my_completed_session):
    # Example 3: Applying custom metadata to a full session
    await my_memory_service.add_session_to_memory(
        session=my_completed_session,
        custom_metadata={
            "category": "user_preference"
        }
    )