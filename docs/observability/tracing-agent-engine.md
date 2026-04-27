# OpenTelemetry Tracing for Agent Engine

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

When deploying an agent to [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview), proper OpenTelemetry (OTEL) configuration is critical for observability. This guide explains the precise initialization sequence, configuration requirements, and infrastructure setup needed to ensure traces are emitted, ingested, and displayed correctly on the Vertex AI dashboard.

!!! warning "Critical: Initialization Order Matters"
    OpenTelemetry tracing initialization **MUST** occur within the `AdkApp.set_up()` method when deploying to Agent Engine. Initializing tracing outside of this lifecycle method will result in blank dashboards and missing traces.

## Why Initialization Order Matters

Agent Engine uses a managed runtime environment that controls the application lifecycle. The `AdkApp` class provides specific lifecycle hooks that ensure proper integration with Vertex AI's telemetry infrastructure:

- **`set_up()`**: Called once during agent initialization - this is where telemetry providers must be configured
- **`register_operations()`**: Declares operations exposed to Agent Engine
- **`async_stream_query()`**: Handles streaming responses with active tracing context

If you initialize OpenTelemetry outside of `set_up()`, the tracing context won't be properly propagated through Agent Engine's managed execution environment, resulting in:

- Blank dashboards in Vertex AI console
- Missing trace data in Cloud Trace
- Disconnected spans that don't form complete traces
- Lost correlation between agent operations and LLM calls

## Architecture Overview

The following diagram illustrates how OpenTelemetry traces flow from your ADK agent through Agent Engine to Cloud Trace and the Vertex AI dashboard:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your ADK Agent Code                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AdkApp.set_up()                                         │  │
│  │    ↓                                                     │  │
│  │  Initialize OpenTelemetry TracerProvider                │  │
│  │    ↓                                                     │  │
│  │  Configure CloudTraceSpanExporter                       │  │
│  │    ↓                                                     │  │
│  │  Set global tracer provider                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Agent Operations (query, stream, etc.)                 │  │
│  │    • Agent execution spans                              │  │
│  │    • LLM call spans                                     │  │
│  │    • Tool execution spans                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              Vertex AI Agent Engine Runtime                     │
│  • Manages application lifecycle                               │
│  • Propagates trace context across operations                  │
│  • Batches and exports spans                                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Trace                           │
│  • Ingests trace spans via OTLP                                │
│  • Stores and indexes trace data                               │
│  • Provides query and analysis APIs                            │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              Vertex AI Dashboard & Log Analyzer                 │
│  • Visualizes agent execution traces                           │
│  • Shows LLM interactions and tool calls                       │
│  • Enables performance analysis                                │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

Before implementing OpenTelemetry tracing for Agent Engine, ensure you have:

1. **Google Cloud Project** with the following APIs enabled:
   - [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
   - [Cloud Trace API](https://console.cloud.google.com/apis/library/cloudtrace.googleapis.com)
   - [Cloud Logging API](https://console.cloud.google.com/apis/library/logging.googleapis.com)

2. **Required Python packages**:
   ```bash
   pip install google-cloud-aiplatform[adk,agent_engines]
   pip install opentelemetry-api
   pip install opentelemetry-sdk
   pip install opentelemetry-exporter-gcp-trace
   ```

3. **Authentication** configured for your environment:
   ```bash
   gcloud auth application-default login
   ```

## Implementation Guide

### Method 1: Using Environment Variables (Recommended)

The simplest way to enable tracing is through environment variables. This method is recommended for most use cases as it requires minimal code changes.

#### Step 1: Set Environment Variables

When deploying to Agent Engine, configure these environment variables:

```python
env_vars = {
    # Enable Agent Engine telemetry
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    
    # Capture full prompt and response content
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
    
    # Set your Google Cloud project ID
    "GOOGLE_CLOUD_PROJECT": "your-project-id",
}
```

**Environment Variable Details:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY` | Enables trace and log collection | `false` |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | Includes prompts and responses in traces | `false` |
| `GOOGLE_CLOUD_PROJECT` | Specifies the project for trace ingestion | Required |

!!! note "Privacy Consideration"
    Setting `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` will log full prompts and model responses. Review your data privacy requirements before enabling this in production.

#### Step 2: Deploy with ADK CLI

```bash
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --staging_bucket=$STAGING_BUCKET \
    --trace_to_cloud \
    path/to/your/agent
```

The `--trace_to_cloud` flag automatically configures the environment variables for you.

#### Step 3: Deploy with Python SDK

```python
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
import vertexai

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-staging-bucket"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Create AdkApp with tracing enabled
adk_app = reasoning_engines.AdkApp(
    agent=your_agent,
    enable_tracing=True,  # This sets the environment variables
)

# Deploy to Agent Engine
remote_app = agent_engines.create(
    agent_engine=adk_app,
    extra_packages=["./your_agent"],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
)
```

### Method 2: Manual OpenTelemetry Configuration

For advanced use cases where you need fine-grained control over tracing configuration, you can manually initialize OpenTelemetry within the `AdkApp.set_up()` method.

#### Complete Example

```python
# agent_engine_app.py

from vertexai.agent_engines.templates.adk import AdkApp
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from google.adk.agents import Agent
import os


# Define your agent
def get_weather(city: str) -> dict:
    """Get weather for a city."""
    return {"city": city, "temperature": "72°F", "condition": "sunny"}


root_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Agent to answer weather questions",
    tools=[get_weather],
)


class WeatherAgentApp(AdkApp):
    """Custom AdkApp with manual OpenTelemetry configuration."""
    
    def set_up(self):
        """
        CRITICAL: Initialize OpenTelemetry here, not in module-level code.
        
        This method is called once during agent initialization in the
        Agent Engine runtime. Initializing tracing here ensures proper
        integration with Vertex AI's telemetry infrastructure.
        """
        # Get project ID from environment
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set")
        
        # Create tracer provider
        provider = TracerProvider()
        
        # Configure Cloud Trace exporter
        cloud_trace_exporter = CloudTraceSpanExporter(
            project_id=project_id
        )
        
        # Use BatchSpanProcessor for efficient span export
        span_processor = BatchSpanProcessor(cloud_trace_exporter)
        provider.add_span_processor(span_processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(provider)
        
        # Call parent set_up to complete initialization
        super().set_up()
    
    def register_operations(self):
        """Register agent operations exposed to Agent Engine."""
        return {
            "query": self.async_stream_query,
        }


# Create app instance
app = WeatherAgentApp(agent=root_agent)
```

#### Deployment Script

```python
# deploy.py

from vertexai import agent_engines
import vertexai
from agent_engine_app import app

PROJECT_ID = "your-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-staging-bucket"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Deploy the custom app
remote_app = agent_engines.create(
    agent_engine=app,
    extra_packages=["./your_agent"],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-exporter-gcp-trace",
    ],
)

print(f"Agent Engine deployed: {remote_app.resource_name}")
```

## Infrastructure Configuration

### Terraform Setup

If you're using Terraform to manage your Agent Engine infrastructure, include these configurations:

```hcl
# terraform/agent_engine.tf

resource "google_vertex_ai_reasoning_engine" "agent" {
  display_name = "weather-agent"
  location     = var.region
  
  # Source code configuration
  source_code_spec {
    # ... your source code configuration
  }
  
  # Environment variables for tracing
  environment_variables = {
    GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY           = "true"
    OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT   = "true"
    GOOGLE_CLOUD_PROJECT                                 = var.project_id
  }
  
  # Ensure APIs are enabled
  depends_on = [
    google_project_service.aiplatform,
    google_project_service.cloudtrace,
    google_project_service.logging,
  ]
}

# Enable required APIs
resource "google_project_service" "aiplatform" {
  service = "aiplatform.googleapis.com"
}

resource "google_project_service" "cloudtrace" {
  service = "cloudtrace.googleapis.com"
}

resource "google_project_service" "logging" {
  service = "logging.googleapis.com"
}
```

### IAM Permissions

Ensure your Agent Engine service account has these permissions:

```hcl
# terraform/iam.tf

resource "google_project_iam_member" "agent_engine_trace_writer" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.agent_engine.email}"
}

resource "google_project_iam_member" "agent_engine_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.agent_engine.email}"
}
```

## Viewing Traces

### Vertex AI Dashboard

After deployment, traces appear in the Vertex AI console:

1. Navigate to [Vertex AI Agent Engine](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
2. Select your Agent Engine instance
3. Click the **Traces** tab
4. Choose between **Session view** or **Span view**

**Session view** groups traces by user session, showing the complete conversation flow.

**Span view** displays individual operations (agent runs, LLM calls, tool executions) with timing and attributes.

### Cloud Trace Explorer

For detailed trace analysis:

1. Navigate to [Cloud Trace](https://console.cloud.google.com/traces)
2. Use filters to find specific traces:
   - Filter by span name: `invocation`, `agent_run`, `call_llm`, `execute_tool`
   - Filter by time range
   - Filter by latency or error status

3. Click on a trace to see:
   - Waterfall view of all spans
   - Timing information for each operation
   - Span attributes (prompts, responses, tool arguments)
   - Error details if any operation failed

### Understanding Trace Structure

A typical ADK agent trace contains these span types:

```
invocation (root span)
├── agent_run
│   ├── call_llm
│   │   └── [LLM request/response details]
│   ├── execute_tool
│   │   └── [Tool execution details]
│   └── call_llm
│       └── [Final response details]
└── [Additional agent operations]
```

**Span Attributes:**

- `invocation`: Session ID, user ID, app name
- `agent_run`: Agent name, model, instruction
- `call_llm`: Prompt, response, token counts, model parameters
- `execute_tool`: Tool name, arguments, result

## Troubleshooting

### Problem: Blank Dashboard / No Traces

**Symptoms:**
- Vertex AI dashboard shows no traces
- Cloud Trace Explorer is empty
- Agent appears to be working correctly

**Solutions:**

1. **Verify initialization order:**
   ```python
   # ❌ WRONG: Initializing at module level
   provider = TracerProvider()
   trace.set_tracer_provider(provider)
   
   class MyApp(AdkApp):
       def set_up(self):
           super().set_up()
   
   # ✅ CORRECT: Initializing in set_up()
   class MyApp(AdkApp):
       def set_up(self):
           provider = TracerProvider()
           trace.set_tracer_provider(provider)
           super().set_up()
   ```

2. **Check environment variables:**
   ```python
   # Verify these are set in your deployment
   import os
   print(os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"))
   print(os.environ.get("GOOGLE_CLOUD_PROJECT"))
   ```

3. **Verify API enablement:**
   ```bash
   gcloud services list --enabled --project=your-project-id | grep -E "aiplatform|cloudtrace|logging"
   ```

4. **Check IAM permissions:**
   ```bash
   gcloud projects get-iam-policy your-project-id \
       --flatten="bindings[].members" \
       --filter="bindings.members:serviceAccount:*agent-engine*"
   ```

### Problem: Incomplete Traces

**Symptoms:**
- Some spans appear but others are missing
- Traces don't show LLM calls or tool executions
- Disconnected spans that don't form a hierarchy

**Solutions:**

1. **Ensure BatchSpanProcessor is used:**
   ```python
   # Use BatchSpanProcessor, not SimpleSpanProcessor
   span_processor = BatchSpanProcessor(cloud_trace_exporter)
   provider.add_span_processor(span_processor)
   ```

2. **Check for exceptions during tracing:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Look for OpenTelemetry-related errors in logs
   ```

3. **Verify trace context propagation:**
   ```python
   from opentelemetry import trace
   
   # In your agent code, verify active span exists
   current_span = trace.get_current_span()
   if current_span.is_recording():
       print("Tracing is active")
   ```

### Problem: Missing Prompt/Response Content

**Symptoms:**
- Traces appear but don't show LLM prompts or responses
- Span attributes are incomplete

**Solution:**

Ensure `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` is set to `"true"`:

```python
env_vars = {
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
}
```

### Problem: High Trace Volume / Cost Concerns

**Symptoms:**
- Large number of traces generated
- Unexpected Cloud Trace costs

**Solutions:**

1. **Implement sampling:**
   ```python
   from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
   
   # Sample 10% of traces
   sampler = TraceIdRatioBased(0.1)
   provider = TracerProvider(sampler=sampler)
   ```

2. **Use environment-based sampling:**
   ```python
   import os
   
   # Sample more in dev, less in prod
   sample_rate = 1.0 if os.environ.get("ENV") == "dev" else 0.1
   sampler = TraceIdRatioBased(sample_rate)
   ```

3. **Review Cloud Trace quotas and pricing:**
   - [Cloud Trace Quotas](https://cloud.google.com/trace/docs/quotas)
   - [Cloud Trace Pricing](https://cloud.google.com/trace/pricing)

## Best Practices

### 1. Always Initialize in set_up()

```python
class MyAgentApp(AdkApp):
    def set_up(self):
        # ✅ Initialize tracing here
        self._configure_tracing()
        super().set_up()
    
    def _configure_tracing(self):
        """Separate method for tracing configuration."""
        provider = TracerProvider()
        # ... configuration
        trace.set_tracer_provider(provider)
```

### 2. Use Environment Variables for Configuration

```python
def set_up(self):
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    enable_content_capture = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", 
        "false"
    ).lower() == "true"
    
    # Configure based on environment
```

### 3. Add Custom Span Attributes

```python
from opentelemetry import trace

def my_custom_operation(self, data):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("operation.type", "data_processing")
        span.set_attribute("data.size", len(data))
        # ... your operation
```

### 4. Handle Tracing Errors Gracefully

```python
def set_up(self):
    try:
        self._configure_tracing()
    except Exception as e:
        # Log error but don't fail deployment
        import logging
        logging.error(f"Failed to configure tracing: {e}")
    
    super().set_up()
```

### 5. Use Sampling in Production

```python
def set_up(self):
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
    
    # Sample based on environment
    is_production = os.environ.get("ENV") == "production"
    sample_rate = 0.1 if is_production else 1.0
    
    provider = TracerProvider(sampler=TraceIdRatioBased(sample_rate))
    # ... rest of configuration
```

## Example: Complete Agent with Tracing

Here's a complete example showing proper OpenTelemetry configuration for Agent Engine:

```python
# weather_agent_app.py

import os
from vertexai.agent_engines.templates.adk import AdkApp
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from google.adk.agents import Agent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define agent tools
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    # Simulate weather API call
    return {
        "city": city,
        "temperature": "72°F",
        "condition": "sunny",
        "humidity": "45%"
    }


def get_forecast(city: str, days: int = 3) -> dict:
    """Get weather forecast for a city."""
    return {
        "city": city,
        "days": days,
        "forecast": ["sunny", "cloudy", "rainy"]
    }


# Create agent
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Agent that provides weather information",
    instruction="Use the available tools to answer weather questions accurately.",
    tools=[get_weather, get_forecast],
)


class WeatherAgentApp(AdkApp):
    """Weather agent with OpenTelemetry tracing."""
    
    def set_up(self):
        """Initialize OpenTelemetry tracing for Agent Engine."""
        logger.info("Initializing Weather Agent with tracing")
        
        try:
            self._configure_tracing()
            logger.info("Tracing configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure tracing: {e}")
            # Continue without tracing rather than failing deployment
        
        # Call parent set_up
        super().set_up()
    
    def _configure_tracing(self):
        """Configure OpenTelemetry with Cloud Trace exporter."""
        # Get configuration from environment
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set")
        
        # Determine sampling rate based on environment
        env = os.environ.get("ENV", "production")
        sample_rate = 1.0 if env == "development" else 0.1
        
        logger.info(f"Configuring tracing for project: {project_id}")
        logger.info(f"Sample rate: {sample_rate}")
        
        # Create tracer provider with sampling
        provider = TracerProvider(
            sampler=TraceIdRatioBased(sample_rate)
        )
        
        # Configure Cloud Trace exporter
        cloud_trace_exporter = CloudTraceSpanExporter(
            project_id=project_id
        )
        
        # Use batch processor for efficiency
        span_processor = BatchSpanProcessor(
            cloud_trace_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
        )
        
        provider.add_span_processor(span_processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(provider)
    
    def register_operations(self):
        """Register operations exposed to Agent Engine."""
        return {
            "query": self.async_stream_query,
        }


# Create app instance for deployment
app = WeatherAgentApp(agent=weather_agent)
```

Deploy this agent:

```bash
adk deploy agent_engine \
    --project=your-project-id \
    --region=us-central1 \
    --staging_bucket=gs://your-bucket \
    --trace_to_cloud \
    weather_agent_app
```

## Additional Resources

- [Cloud Trace Documentation](https://cloud.google.com/trace/docs)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
- [Vertex AI Agent Engine Overview](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
- [ADK Observability Integration](https://google.github.io/adk-docs/integrations/?topic=observability)
- [Agent Starter Pack](https://github.com/google/adk-samples) - Reference implementation with tracing

## Related Documentation

- [Agent Activity Logging](/adk-docs/observability/logging/) - Configure logging for ADK agents
- [Deploy to Agent Engine](/adk-docs/deploy/agent-engine/) - Standard deployment guide
- [Cloud Trace Integration](/adk-docs/integrations/cloud-trace/) - Alternative tracing setup methods
- [AgentOps Integration](/adk-docs/integrations/agentops/) - Third-party observability platform
