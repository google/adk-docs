import google.auth
from google.auth.transport.requests import Request
from google.adk.integrations.agent_registry import AgentRegistry

def google_auth_header_provider(context):
    creds, _ = google.auth.default()
    if not creds.valid:
        creds.refresh(Request())
    return {"Authorization": f"Bearer {creds.token}"}

registry = AgentRegistry(
    project_id=project_id,
    location=location,
    header_provider=google_auth_header_provider
)