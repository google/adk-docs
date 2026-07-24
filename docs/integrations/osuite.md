---
catalog_title: OSuite
catalog_description: Govern ADK tool calls with action review, approvals, and audit evidence
catalog_icon: /integrations/assets/osuite.svg
catalog_tags: ["security", "governance", "mcp"]
---

# OSuite governance for ADK tool calls

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[OSuite](https://osuite.ai) is a governance control plane for AI agents. It
reviews planned work before an agent executes a tool, routes higher-risk actions
to approval, and returns audit-ready records that teams can replay later.

With ADK, OSuite can be used from a `before_tool_callback`: the callback builds a
small action envelope from the tool name, arguments, and business goal, sends it
to OSuite's remote MCP endpoint, and then either lets the tool run or returns a
structured result that skips execution.

## Use cases

- **Approval before side effects**: Pause customer-facing, production, or
  irreversible tool calls until OSuite returns approval.
- **Action-bound evidence**: Bind the review decision to the exact proposed
  action, tool arguments, target system, and policy context.
- **Runtime audit trail**: Record the final outcome after execution so operators
  can replay what was approved, what ran, and what evidence was produced.

## Prerequisites

- Python >= 3.10
- [ADK](https://adk.dev)
- An OSuite workspace with an enabled remote MCP connector
- An OSuite connector access token allowed to call `review_planned_work`

## Use with agent

The example below guards a high-risk `send_customer_update` tool. If OSuite
allows the action, the callback returns `None` and ADK runs the tool normally.
If OSuite requires approval or blocks the action, the callback returns a
dictionary; ADK treats that dictionary as the tool result and skips the tool
execution.

```python
import json
import os
import urllib.request
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

OSUITE_MCP_URL = "https://studio.osuite.ai/api/connectors/osuite/mcp"
OSUITE_ACCESS_TOKEN = os.environ["OSUITE_ACCESS_TOKEN"]


def call_osuite_review(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": "adk-osuite-review",
        "method": "tools/call",
        "params": {
            "name": "review_planned_work",
            "arguments": {
                "goal": "Review an ADK tool call before execution.",
                "proposed_action": f"Run ADK tool {tool_name}",
                "action_kind": "external_tool_call",
                "risk_level": 70,
                "reversible": False,
                "tool_name": tool_name,
                "tool_category": "adk_tool",
                "tool_input": args,
                "systems_touched": "customer support workspace",
                "decision_context": json.dumps(
                    {
                        "runtime": "google-adk",
                        "tool_name": tool_name,
                        "tool_args": args,
                    },
                    sort_keys=True,
                ),
            },
        },
    }

    request = urllib.request.Request(
        OSUITE_MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OSUITE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        body = json.loads(response.read().decode("utf-8"))

    if "error" in body:
        raise RuntimeError(body["error"])
    return body["result"]["structuredContent"]


def osuite_before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    decision = call_osuite_review(tool.name, args)

    if decision.get("blocked"):
        return {
            "status": "blocked_by_osuite",
            "action_id": decision.get("action_id"),
            "reason": decision.get("user_message"),
            "audit_record": decision.get("audit_record"),
        }

    if decision.get("approval_required"):
        return {
            "status": "waiting_for_osuite_approval",
            "action_id": decision.get("action_id"),
            "reason": decision.get("user_message"),
            "audit_record": decision.get("audit_record"),
        }

    tool_context.state["osuite:last_action_id"] = decision.get("action_id")
    return None


def send_customer_update(case_id: str, message: str) -> Dict[str, Any]:
    """Send a customer-support update."""
    return {"case_id": case_id, "sent": True, "message": message}


customer_update_tool = FunctionTool(func=send_customer_update)

root_agent = LlmAgent(
    name="governed_support_agent",
    model="gemini-flash-latest",
    instruction=(
        "Help support operators draft and send customer updates. "
        "Use the customer update tool only after OSuite review allows it."
    ),
    tools=[customer_update_tool],
    before_tool_callback=osuite_before_tool_callback,
)
```

After the tool finishes, applications can call OSuite's `record_final_outcome`
tool through the same remote MCP endpoint to close the audit record.

## Additional resources

- [OSuite](https://osuite.ai)
- [OSuite privacy policy](https://osuite.ai/privacy)
- [ADK callbacks](https://adk.dev/callbacks/)
- [ADK tool callbacks](https://adk.dev/callbacks/types-of-callbacks/#before-tool-callback)
