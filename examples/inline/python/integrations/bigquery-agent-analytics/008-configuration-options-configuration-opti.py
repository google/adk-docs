config = BigQueryLoggerConfig(
    enable_otel_correlation=True,                      # join key against Cloud Trace
    custom_metadata_allowlist=["ticket_id", "exp:*"],  # capture selected custom_metadata keys
    # payload_column_denylist=["content_parts"],       # don't persist multimodal payloads
)