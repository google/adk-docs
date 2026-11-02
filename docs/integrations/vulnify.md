---
catalog_title: Vulnify
catalog_description: Check every tool call and allow, hold for review, or block it
catalog_icon: /integrations/assets/vulnify.png
---

# Vulnify plugin for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Vulnify](https://www.vulnify.io) checks an agent's action before it runs and
answers `ALLOW`, `REVIEW`, or `BLOCK` in real time, writing each decision to an
audit log. With ADK, an `LlmAgent` sets `before_tool_callback`, and that
callback calls `Vulnify.guard` from the Vulnify Python SDK before every tool
call.

- `ALLOW`: the callback returns `None` and ADK runs the tool.
- `BLOCK`: the callback returns a refusal dict. ADK uses it as the tool result,
  so the tool does not run and the model sees the refusal.
- `REVIEW`: the tool does not run and the model is told the action is pending
  human review. The process can wait until a person approves or denies it in
  the Vulnify app or in Slack.

## Use cases

- **Hold risky exports for a person**: Send bulk data exports to external
  destinations to human review before they run.
- **Block destructive actions**: Stop calls such as deleting a production
  database, according to policies you set in Vulnify.
- **Audit every tool call**: Keep a record of each decision the agent asked
  for, with the action, resource, and outcome.

## Prerequisites

- Python >= 3.10
- [ADK](https://adk.dev) >= 2.0.0
- A Vulnify API key (`VULNIFY_API_KEY`) from the
  [Vulnify app](https://app.vulnify.io). Not needed for the mock run below.
- A Gemini API key (`GOOGLE_API_KEY`) if a live model should choose the tool
  calls. Not needed for the mock run below.

## Installation

```bash
pip install vulnify google-adk
```

## Use with agent

The callback maps each tool call to an action description and asks Vulnify
before the tool runs. ADK passes callback arguments by keyword, so the
parameters must be named `tool`, `args`, and `tool_context`.

```python
from google.adk.agents import Agent
from vulnify import Vulnify, VulnifyBlockedError


def export_customers(email: str, rows: int) -> str:
    """Export customer records and email them to an address."""
    return f"exported {rows} customers to {email}"


def describe_export(args: dict) -> dict:
    return {
        "agent": "support-agent",
        "action": "EXPORT_DATA",
        "resource": "Customer Database",
        "destination": "EXTERNAL_EMAIL",
        "records_affected": int(args.get("rows") or 0),
    }


DESCRIBE = {"export_customers": describe_export}


def guard_tool_calls(vulnify, wait=None):
    def before_tool_callback(tool, args, tool_context):
        describe = DESCRIBE.get(getattr(tool, "name", ""))
        if describe is None:
            return None
        try:
            vulnify.guard(lambda: None, wait=wait, **describe(dict(args or {})))
        except VulnifyBlockedError as err:
            decision = err.result.final_decision or err.result.decision
            suffix = "Pending human review." if decision == "REVIEW" else "Refused."
            return {"result": f"{err}. {suffix}"}
        return None  # ALLOW: ADK runs the tool

    return before_tool_callback


vulnify = Vulnify(api_key="YOUR_VULNIFY_API_KEY", fail_mode="closed")

root_agent = Agent(
    name="ops_assistant",
    model="gemini-flash-latest",
    instruction="You are an ops assistant. Use the tools you are given.",
    tools=[export_customers],
    before_tool_callback=guard_tool_calls(vulnify),
)
```

Pass `wait={"timeout": 120}` to `guard_tool_calls` when the process should
wait for a person to approve or deny a `REVIEW`. Without `wait`, `REVIEW`
returns immediately and the tool stays unrun.

## Run the example without keys

The [complete example](https://github.com/vulnify/vulnify-examples/tree/main/google-adk)
includes a mock mode with a scripted model and local decisions, so it needs no
API keys. It walks three calls: reading a project file is allowed, exporting
800 customer records to an external email is held for review, and deleting a
production database is blocked.

```bash
git clone https://github.com/vulnify/vulnify-examples.git
cd vulnify-examples/google-adk
pip install -r requirements.txt
python main.py --mock
```

Output:

```
Mock mode: no API call. A file read is ALLOW, the export is REVIEW, the delete is BLOCK.
read_file: contents of README.md
export_customers: Vulnify REVIEW: Export operation; External destination; Large data volume (800 records). Pending human review.
delete_production_database: Vulnify BLOCK: Delete operation; Production database. Refused.
side effects: ['read_file README.md']
```

In live mode, set `VULNIFY_API_KEY` (and `GOOGLE_API_KEY` to let Gemini choose
the calls). Live `BLOCK` decisions come from the policies you create in the
Vulnify app.

## Resources

- [Vulnify](https://www.vulnify.io)
- [Google ADK example](https://github.com/vulnify/vulnify-examples/tree/main/google-adk)
- [Vulnify Python SDK on PyPI](https://pypi.org/project/vulnify/)
