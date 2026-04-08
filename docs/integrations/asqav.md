---
catalog_title: Asqav
catalog_description: Tamper-evident audit trails and policy enforcement for ADK agents
catalog_icon: /integrations/assets/asqav.png
catalog_tags: ["governance", "security"]
---

# Asqav governance for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Asqav](https://asqav.com) provides governance for AI agents - signed audit
trails, policy enforcement, and compliance reporting. Every agent action gets a
quantum-safe ML-DSA-65 signature hash-chained to the previous one, creating a
tamper-evident log. If entries are modified or omitted, the chain breaks and
verification fails.

Asqav integrates with ADK through the `before_agent_callback` and
`after_agent_callback` hooks on `BaseAgent`, signing agent lifecycle events
without interfering with agent execution.

## Use cases

- **Audit trails** - cryptographically signed record of every agent run, with
  verifiable timestamps and chain integrity
- **Policy enforcement** - block or alert on agent actions that violate
  governance rules before execution begins
- **Compliance reporting** - automated exports for EU AI Act and DORA
  requirements

## Prerequisites

- Python 3.10+
- An asqav API key (free tier available at [asqav.com](https://asqav.com))

## Installation

```bash
pip install asqav google-adk
```

## Setup

Set your API keys as environment variables:

```bash
export ASQAV_API_KEY="sk_..."
export GOOGLE_API_KEY="your-gemini-api-key"
```

Initialize asqav at the start of your application:

```python
import asqav

asqav.init(api_key="sk_...")
```

## Use with agent

Asqav plugs into ADK's `before_agent_callback` and `after_agent_callback` on
any agent that inherits from `BaseAgent`. The callbacks sign each agent
invocation as a governance event and return `None`, so normal agent execution
continues uninterrupted.

### Basic callback integration

```python
import asqav
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

asqav.init(api_key="sk_...")
governance_agent = asqav.Agent.create("my-adk-agent")


def asqav_before_callback(callback_context):
    """Sign agent:start before the agent runs."""
    governance_agent.sign("agent:start", {
        "agent": callback_context.agent_name,
        "session_id": callback_context.session.id,
    })
    return None  # Continue normal execution


def asqav_after_callback(callback_context):
    """Sign agent:end after the agent completes."""
    governance_agent.sign("agent:end", {
        "agent": callback_context.agent_name,
        "session_id": callback_context.session.id,
    })
    return None  # Do not modify agent output


agent = Agent(
    name="governed_agent",
    model="gemini-2.0-flash",
    description="An agent with asqav audit trails.",
    instruction="You are a helpful assistant.",
    before_agent_callback=asqav_before_callback,
    after_agent_callback=asqav_after_callback,
)

runner = InMemoryRunner(agent=agent, app_name="governed_app")
```

### Policy enforcement with before_agent_callback

Use `before_agent_callback` to check asqav policies before the agent runs. If a
policy blocks the action, return a `types.Content` response to skip agent
execution entirely:

```python
from google.genai import types

asqav.init(api_key="sk_...")
governance_agent = asqav.Agent.create("policy-enforced-agent")


def asqav_policy_gate(callback_context):
    """Check policy before allowing agent execution."""
    try:
        result = governance_agent.sign("agent:start", {
            "agent": callback_context.agent_name,
            "action": "execute",
        })
        return None  # Policy allows execution, proceed normally
    except asqav.AsqavError as e:
        # Policy blocked this action - skip agent execution
        return types.Content(
            role="model",
            parts=[types.Part(text=f"Action blocked by governance policy: {e}")],
        )


agent = Agent(
    name="policy_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant.",
    before_agent_callback=asqav_policy_gate,
)
```

### Async callback support

ADK supports both sync and async callbacks. Use `AsyncAgent` for async signing:

```python
import asqav
from google.adk.agents import Agent

asqav.init(api_key="sk_...")
governance_agent = await asqav.AsyncAgent.create("async-adk-agent")


async def asqav_before_async(callback_context):
    """Async signing for agent:start."""
    await governance_agent.sign("agent:start", {
        "agent": callback_context.agent_name,
    })
    return None


async def asqav_after_async(callback_context):
    """Async signing for agent:end."""
    await governance_agent.sign("agent:end", {
        "agent": callback_context.agent_name,
    })
    return None


agent = Agent(
    name="async_governed_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant.",
    before_agent_callback=asqav_before_async,
    after_agent_callback=asqav_after_async,
)
```

### Multi-agent governance

When using `SequentialAgent`, `ParallelAgent`, or other multi-agent patterns,
attach asqav callbacks to each agent in the tree to get a complete audit trail:

```python
from google.adk.agents import Agent, SequentialAgent

asqav.init(api_key="sk_...")
governance_agent = asqav.Agent.create("multi-agent-workflow")


def make_audit_callbacks(agent_role):
    """Create before/after callbacks for a specific agent role."""

    def before_cb(callback_context):
        governance_agent.sign("agent:start", {
            "agent": callback_context.agent_name,
            "role": agent_role,
        })
        return None

    def after_cb(callback_context):
        governance_agent.sign("agent:end", {
            "agent": callback_context.agent_name,
            "role": agent_role,
        })
        return None

    return before_cb, after_cb


research_before, research_after = make_audit_callbacks("researcher")
writer_before, writer_after = make_audit_callbacks("writer")

researcher = Agent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="Research the given topic.",
    before_agent_callback=research_before,
    after_agent_callback=research_after,
)

writer = Agent(
    name="writer",
    model="gemini-2.0-flash",
    instruction="Write a summary based on the research.",
    before_agent_callback=writer_before,
    after_agent_callback=writer_after,
)

pipeline_before, pipeline_after = make_audit_callbacks("pipeline")

pipeline = SequentialAgent(
    name="research_pipeline",
    sub_agents=[researcher, writer],
    before_agent_callback=pipeline_before,
    after_agent_callback=pipeline_after,
)
```

### Verifying the audit trail

After running your agent, verify the integrity of the signed audit trail:

```python
# Export audit trail as JSON
audit = asqav.export_audit_json(agent_id=governance_agent.id)

# Verify a specific signature
verification = asqav.verify_signature(signature_id="sig_abc123")
print(verification.valid)  # True if chain is intact

# Export as CSV for compliance reporting
asqav.export_audit_csv(agent_id=governance_agent.id, output="audit.csv")
```

## How it works

Asqav uses ADK's callback system to intercept agent lifecycle events:

1. **before_agent_callback** fires immediately before the agent's core logic
   runs. Asqav signs an `agent:start` event and optionally checks governance
   policies. Returning `None` allows normal execution. Returning
   `types.Content` skips the agent entirely.

2. **after_agent_callback** fires immediately after the agent completes. Asqav
   signs an `agent:end` event to close the audit record. Returning `None`
   preserves the agent's original output.

Each signed action produces a `SignatureResponse` containing the ML-DSA-65
signature, a `chain_hash` linking it to the previous entry, and a `verify_url`
for independent verification.

Signing failures are logged but never raise exceptions - governance must not
break your AI pipeline.

## Resources

- [Asqav Documentation](https://asqav.com/docs)
- [Asqav SDK on GitHub](https://github.com/jagmarques/asqav-sdk)
- [Asqav on PyPI](https://pypi.org/project/asqav/)
- [ADK Callbacks Guide](https://google.github.io/adk-docs/callbacks/)
