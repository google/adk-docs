import json
import uuid

import functions_framework
import requests

AGENT_URL = "https://my-agent-service-xxxxx.run.app"

@functions_framework.http
def handle_webhook(request):
    """Cloud Run function that receives webhooks and forwards to the agent."""
    payload = request.get_json(silent=True) or {}

    requests.post(
        f"{AGENT_URL}/run",
        json={
            "app_name": "my_agent",
            "user_id": payload.get("account", "webhook-caller"),
            "session_id": str(uuid.uuid4()),
            "new_message": {
                "role": "user",
                "parts": [{"text": json.dumps(payload)}],
            },
        },
    )

    return ("ok", 200)