import com.google.common.collect.ImmutableList;

BigQueryLoggerConfig config = BigQueryLoggerConfig.builder()
    .eventDenylist(ImmutableList.of(
        "HITL_CREDENTIAL_REQUEST",
        "HITL_CREDENTIAL_REQUEST_COMPLETED"
    ))
    // ... other options
    .build();