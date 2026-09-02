run_config = RunConfig(
    # Limit total LLM calls per invocation
    max_llm_calls=500,  # Default: 500 (prevents runaway loops)
                        # 0 or negative = unlimited (use with caution)

    # Save audio/video artifacts for debugging/compliance
    save_live_blob=True,  # Default: False

    # Attach custom metadata to events
    custom_metadata={"user_tier": "premium", "session_type": "support"},  # Default: None

    # Enable compositional function calling (experimental)
    support_cfc=True  # Default: False (Gemini 2.x models only)
)