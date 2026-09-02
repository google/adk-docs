from google.adk.integrations.eventarc import (
    CloudEventAttributesBinding,
    MISSING,
    OMIT,
)

# 1. Using MISSING (default): CloudEvent automatically includes the current UTC timestamp
binding_with_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=MISSING,  # Results in "time": "2026-07-31T20:20:00Z"
)

# 2. Using OMIT: CloudEvent will NOT include a 'time' attribute
binding_without_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=OMIT,  # The 'time' field is excluded from the published event
)