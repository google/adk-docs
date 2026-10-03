---
catalog_title: LoopGrid
catalog_description: Record signed, independently verifiable evidence for consequential ADK agent decisions
catalog_icon: /integrations/assets/loopgrid.png
---

# LoopGrid plugin for ADK

LoopGrid provides a native Google Agent Development Kit (ADK) plugin for recording signed, independently verifiable evidence around consequential AI-agent decisions. It observes the ADK plugin lifecycle while keeping application-owned claims—such as delegated authority, policy decisions, external action execution, and business outcomes—explicit.

LoopGrid records and verifies evidence. It does not execute refunds, payments, account mutations, or other external business actions.

## Use cases

- **Agent governance and audit evidence**: Preserve who or what made a decision, the delegated authority and policy applied by the application, and the resulting agent lifecycle evidence.
- **Consequential tool-use evidence**: Record ADK tool requests and framework-observed tool results without automatically claiming that an external business action executed.
- **Outcome verification**: Let the application explicitly record authoritative action execution and downstream outcomes, then verify the signed LoopGrid evidence chain independently.
- **Privacy-conscious evidence capture**: Record SHA-256 commitments and bounded metadata by default instead of raw user, model, tool, or exception content.

## Prerequisites

- Python 3.10 or later
- Google ADK 2.10.0 or later
- A reachable LoopGrid Core endpoint
- A LoopGrid workspace and API key if your LoopGrid deployment requires authentication
- A model provider configured for your ADK agent (for example, a Gemini API key when using Gemini)

## Installation

```bash
pip install loopgrid-google-adk
```

## Configure LoopGrid

Set the LoopGrid connection values as environment variables:

```bash
export LOOPGRID_BASE_URL="http://127.0.0.1:8000"
export LOOPGRID_WORKSPACE_ID="default"
export LOOPGRID_API_KEY="YOUR_LOOPGRID_API_KEY"
```

If you use Gemini for the example agent, also configure your model provider:

```bash
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

## Use with agent

The plugin is registered through ADK's native `App(plugins=[...])` interface.

```python
import asyncio

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types

from loopgrid_google_adk import LoopGridADKPlugin


async def main():
    plugin = LoopGridADKPlugin(
        authority={
            "scope": "refunds",
            "max_amount": 50,
            "currency": "USD",
        },
        policy={
            "policy_id": "refund-policy-v3",
            "decision": "auto_allowed",
        },
        proposed_action={
            "type": "refund",
            "amount": 25,
            "currency": "USD",
        },
        context={"prompt_version": "support-v7"},
    )

    executed = {}

    def sandbox_refund(amount: float, currency: str) -> dict:
        """Execute a sandbox refund. No real money is moved."""
        executed.update(
            {
                "tool": "sandbox_refund",
                "amount": amount,
                "currency": currency,
                "status": "sandbox_refunded",
                "external_ref": "sandbox-refund-001",
                "sandbox": True,
                "real_money_moved": False,
            }
        )
        return dict(executed)

    agent = Agent(
        name="refund_support_agent",
        model="gemini-2.5-flash",
        instruction=(
            "Use sandbox_refund for the requested sandbox refund, then report "
            "that the sandbox workflow completed."
        ),
        tools=[sandbox_refund],
    )

    app = App(
        name="loopgrid_adk_refund_demo",
        root_agent=agent,
        plugins=[plugin],
    )
    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        app_name=app.name,
        user_id="sandbox-user",
        session_id="loopgrid-adk-refund-session",
    )

    run_id = plugin.bind_run("adk-refund-demo-001")

    async for _event in runner.run_async(
        user_id="sandbox-user",
        session_id=session.id,
        invocation_id=run_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part.from_text(text="Refund the sandbox order for USD 25.")],
        ),
    ):
        pass

    # ADK observed a tool result through its callback lifecycle. The application
    # separately records authoritative evidence that its sandbox tool body ran.
    await plugin.record_action_executed(run_id, executed)

    # The application also owns the authoritative downstream outcome claim.
    await plugin.observe_outcome(
        run_id,
        {
            "status": executed["status"],
            "external_ref": executed["external_ref"],
            "sandbox": True,
            "real_money_moved": False,
        },
    )

    decision = await plugin.get_decision(run_id)
    verification = await plugin.verify_workspace()

    print(decision)
    print(verification)


asyncio.run(main())
```

## Evidence model

LoopGrid maps ADK lifecycle observations to evidence without inferring application-owned facts:

| ADK / application event | LoopGrid evidence |
| --- | --- |
| `before_run_callback` | `decision_created` |
| `after_model_callback` | `model_completed` |
| Explicit application policy | `policy_evaluated` |
| `before_tool_callback` | `tool_requested` |
| `after_tool_callback` | `tool_result` |
| `record_action_executed(...)` | `tool_executed` |
| `observe_outcome(...)` | `outcome_observed` |

### Why a tool result is not automatically an execution claim

ADK callbacks can short-circuit a tool call by returning a response before the underlying tool body executes. For that reason, LoopGrid records `after_tool_callback` as a framework-observed `tool_result`, not automatically as `tool_executed`.

When the application has authoritative evidence that the consequential action actually ran, it records that fact explicitly with `record_action_executed(...)`. The application similarly records authoritative downstream outcomes with `observe_outcome(...)`.

## Privacy and failure behavior

Raw content capture is disabled by default:

```python
LoopGridADKPlugin(capture_content=False)
```

The integration records SHA-256 commitments and bounded metadata instead of raw user content, model responses, tool arguments, tool results, and exception messages unless content capture is explicitly enabled.

The default failure mode is fail-closed (`fail_open=False`), so evidence-required paths surface recording failures instead of silently proceeding without evidence. Applications can opt into fail-open behavior for lower-risk telemetry use cases.

## Additional resources

- [LoopGrid Google ADK integration documentation](https://loopgrid.io/integrations/google-adk/)
- [LoopGrid Google ADK plugin on PyPI](https://pypi.org/project/loopgrid-google-adk/)
- [LoopGrid Google ADK plugin source](https://github.com/loopgridio/loopgrid-google-adk)
- [LoopGrid](https://loopgrid.io/)
