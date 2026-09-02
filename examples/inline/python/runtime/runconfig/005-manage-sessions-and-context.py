from google.adk.agents.run_config import RunConfig
from google.adk.sessions.base_session_service import GetSessionConfig

config = RunConfig(
    get_session_config=GetSessionConfig(num_recent_events=50),
)