import json
import re
from typing import Any

SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

def redact_credentials(event_content: Any, event_type: str) -> str:
    """Redact OAuth secrets and tokens from logged content."""
    if isinstance(event_content, dict):
        text = json.dumps(event_content)
    else:
        text = str(event_content)

    for key in SENSITIVE_KEYS:
        # Redact values in JSON-like strings: "client_secret": "GOCSPX-xxx"
        text = re.sub(
            rf'("{key}"\s*:\s*)"[^"]*"',
            rf'\1"[REDACTED]"',
            text,
            flags=re.IGNORECASE,
        )
    return text

config = BigQueryLoggerConfig(
    content_formatter=redact_credentials,
    # ... other options
)