config = BigQueryLoggerConfig(
    event_denylist=[
        "HITL_CREDENTIAL_REQUEST",
        "HITL_CREDENTIAL_REQUEST_COMPLETED",
    ],
    # ... other options
)