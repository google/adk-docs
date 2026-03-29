---
catalog_title: Aegis
catalog_description: Governance runtime with prompt injection detection, PII masking, and policy-as-code for ADK agents
catalog_icon: /adk-docs/integrations/assets/aegis.svg
catalog_tags: ["safety"]
---

# Aegis governance for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Aegis](https://github.com/Acacian/aegis) is an open-source governance runtime
that auto-instruments Google ADK agents with security guardrails. With a single
function call, Aegis adds prompt injection detection, PII masking, and
policy-as-code enforcement to your agents — no code changes required.

## Use cases

- **Prompt Injection Detection**: Detect and block prompt injection attacks with
  107 detection patterns across 13 categories.

- **PII Masking**: Automatically redact sensitive data such as emails, phone
  numbers, and SSNs from agent inputs and outputs.

- **Policy-as-Code**: Define governance rules in YAML and enforce them with
  `aegis plan` and `aegis test` CLI commands.

- **Audit Trail**: Maintain a complete log of all LLM interactions for
  compliance and debugging.

## Prerequisites

- Python 3.10 or later
- Google ADK installed (`google-adk`)

## Installation

Install Aegis alongside ADK:

```bash
pip install agent-aegis google-adk
```

## Use with agent

```python
import aegis
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Auto-instrument all supported frameworks including Google ADK
aegis.auto_instrument()

agent = Agent(
    model="gemini-2.0-flash",
    name="assistant",
    instruction="You are a helpful assistant.",
)

runner = Runner(
    agent=agent,
    app_name="my_app",
    session_service=InMemorySessionService(),
)
```

All agent interactions are now governed by Aegis guardrails automatically.

## Policy configuration

Define governance policies in a YAML file:

```yaml
# policy.yaml
version: "1.0"
guardrails:
  injection_detection:
    enabled: true
    action: block
  pii_masking:
    enabled: true
    mask_types: [email, phone, ssn]
```

Load the policy when initializing Aegis:

```python
import aegis

aegis.auto_instrument()
aegis.init(policy_path="policy.yaml")
```

Validate and test policies with the Aegis CLI:

```bash
aegis plan   # Preview policy changes
aegis test   # Run policy test suite
```

## Key features

Feature | Description
---- | -----------
Auto-instrumentation | One-line setup with `aegis.auto_instrument()`, no code changes needed
Prompt injection detection | 107 detection patterns across 13 categories
PII masking | Automatic redaction of emails, phone numbers, SSNs, and other sensitive data
Policy-as-code | YAML-based governance rules with `aegis plan` and `aegis test` CLI
Audit trail | Complete log of all LLM interactions for compliance

## Resources

- [Aegis Documentation](https://acacian.github.io/aegis/)
- [Aegis on PyPI](https://pypi.org/project/agent-aegis/)
- [Aegis GitHub Repository](https://github.com/Acacian/aegis)
