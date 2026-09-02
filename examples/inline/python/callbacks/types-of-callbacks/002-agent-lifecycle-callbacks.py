root_agent = LlmAgent(
    name="my_agent",
    model="gemini-flash-latest",
    before_model_callback=[check_policy, log_request],
)