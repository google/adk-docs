ToolSimulationConfig(
    tool_name="send_notification",
    injection_configs=[
        # Always fail for a known-bad recipient
        InjectionConfig(
            match_args={"recipient_id": "INVALID"},
            injected_error=InjectedError(
                injected_http_error_code=400,
                error_message="Invalid recipient.",
            ),
        ),
    ],
    # For all other recipients, generate a plausible success response
    mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
)