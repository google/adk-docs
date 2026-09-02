# Requires: pip install google-adk[gcp]
# Plus environment variable setup:
# GOOGLE_GENAI_USE_ENTERPRISE=TRUE
# GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
from google.adk.sessions import VertexAiSessionService

# The app_name used with this service should be the Reasoning Engine ID or name
APP_ID = "your-reasoning-engine-id"

# Project and location are not required when initializing with Agent Platform express mode
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# Use REASONING_ENGINE_APP_ID when calling service methods, e.g.:
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)