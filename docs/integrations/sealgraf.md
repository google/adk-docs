---
catalog_title: Sealgraf
catalog_description: Owner approval and sealed, publicly verifiable receipts for agent spending
catalog_icon: /integrations/assets/sealgraf.png
catalog_tags: ["mcp"]
---

# Sealgraf MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Sealgraf](https://sealgraf.com) is the approval and evidence layer for
AI-agent spending: "Every dollar, seen and sealed." Before an agent buys,
it checks with Sealgraf. Inside the owner's pre-set limits the purchase
proceeds; above them, the owner approves or denies on Sealgraf's own
surface. Every approval and every denial is sealed into a tamper-evident
receipt that anyone can verify on a public checker, with no account.

## Use cases

- **Gate agent purchases on owner approval**: An agent checks permission
  before spending; above-limit purchases wait for the owner instead of
  going through on the agent's say-so.
- **Produce evidence for every spend**: Each completed purchase seals a
  receipt recording the action, the decision, the authorized amount and
  the amount actually charged — verifiable by anyone from a public link.
- **Audit denials, not just purchases**: A denied purchase seals the same
  quality of evidence, so "the agent tried and was stopped" is provable.

## Prerequisites

- A free [Sealgraf](https://sealgraf.com) account and an agent API key
  (sign up, set your spending limits, create an agent key)

## Use with agent

=== "Python"

    ```python
    import os
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    root_agent = Agent(
        model="gemini-flash-latest",
        name="sealgraf_agent",
        instruction=(
            "Before buying anything, call check_permission. If the outcome "
            "is needs_human_approval, call check_status until the owner "
            "decides. After a purchase completes, call report_purchase. "
            "Never buy after a deny."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://sealgraf.com/mcp",
                    headers={
                        "Authorization": f"Bearer {os.environ['SEALGRAF_API_KEY']}",
                    },
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "sealgraf_agent",
        instruction:
            "Before buying anything, call check_permission. If the outcome " +
            "is needs_human_approval, call check_status until the owner " +
            "decides. After a purchase completes, call report_purchase. " +
            "Never buy after a deny.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://sealgraf.com/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            Authorization: `Bearer ${process.env.SEALGRAF_API_KEY}`,
                        },
                    },
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## Available tools

Tool | Description
---- | -----------
`check_permission` | Ask before a purchase: returns allow (with a single-use decision token), deny, or needs_human_approval under the owner's limits
`check_status` | Read a check's current state while an above-limit purchase waits for the owner
`report_purchase` | Report the completed purchase; Sealgraf seals it into a receipt
`get_receipt` | Read a sealed receipt

## Resources

- [Sealgraf](https://sealgraf.com)
- [Protocol — IETF draft draft-gunuganti-agent-approval-evidence-00](https://datatracker.ietf.org/doc/draft-gunuganti-agent-approval-evidence/)
- Support: support@sealgraf.com
