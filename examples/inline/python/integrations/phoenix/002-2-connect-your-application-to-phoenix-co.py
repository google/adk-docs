from phoenix.otel import register

# Configure the Phoenix tracer
tracer_provider = register(
    project_name="my-llm-app",  # Default is 'default'
    auto_instrument=True        # Auto-instrument your app based on installed OI dependencies
)