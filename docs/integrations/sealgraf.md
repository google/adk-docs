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

[Sealgraf](https://sealgraf.com) is a hosted approval and evidence
service for AI-agent spending. An agent checks a proposed purchase
against an owner-set spending mandate. Purchases requiring approval
wait for the owner in Sealgraf. The agent pays through its own
payment channel and reports the completed purchase to seal a
receipt. Anyone with the verification link can check the receipt
without an account. The public view shows the purchase category,
while amounts and purchase details remain visible to the signed-in
owner.

## Use cases

- **Gate agent purchases on owner approval**: An agent checks
  permission before spending. Purchases requiring approval wait for
  the owner; purchases outside the mandate's limits are denied.
- **Produce evidence for completed purchases**: Each completed
  purchase seals a receipt recording the action, the decision, the
  authorized amount, and the completion amount reported by the
  agent. Anyone with the verification link can check the receipt —
  the public view shows the purchase category, while amounts and
  purchase details remain visible to the signed-in owner.
- **Review permission decisions**: Retain a tamper-evident history
  of permission checks and owner decisions.

## Prerequisites

- A free [Sealgraf](https://sealgraf.com) account and an agent API key
  (sign up, set your spending limits, create an agent key)

## Use with agent

These examples configure Sealgraf's tools only. Purchase execution
requires a separately configured payment tool.

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
            "Before buying, call check_permission. If "
            "needs_human_approval, stop, retain the preauth_id, and "
            "tell the owner. After the owner says they decided, call "
            "check_status. Proceed only on allow or approved, before "
            "the returned deadline. Never buy on denied, declined, "
            "expired, or waiting_for_owner; never repeat a completed "
            "purchase. After payment through the agent's separately "
            "configured payment channel succeeds, call report_purchase "
            "with the preauth_id, actual completed_amount_minor, and "
            "required note. For an immediate allow, also pass the "
            "returned decision_token. After owner approval, omit "
            "decision_token as the tool instructs."
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

    const apiKey = process.env.SEALGRAF_API_KEY;
    if (!apiKey) {
        throw new Error("SEALGRAF_API_KEY environment variable is not set");
    }

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "sealgraf_agent",
        instruction:
            "Before buying, call check_permission. If " +
            "needs_human_approval, stop, retain the preauth_id, and " +
            "tell the owner. After the owner says they decided, call " +
            "check_status. Proceed only on allow or approved, before " +
            "the returned deadline. Never buy on denied, declined, " +
            "expired, or waiting_for_owner; never repeat a completed " +
            "purchase. After payment through the agent's separately " +
            "configured payment channel succeeds, call report_purchase " +
            "with the preauth_id, actual completed_amount_minor, and " +
            "required note. For an immediate allow, also pass the " +
            "returned decision_token. After owner approval, omit " +
            "decision_token as the tool instructs.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://sealgraf.com/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            Authorization: `Bearer ${apiKey}`,
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
`check_permission` | Ask before a purchase: returns allow (with a single-use decision token), needs_human_approval when the purchase requires owner approval, or deny when it falls outside the mandate's limits
`check_status` | Read a check's current state; use it after the owner says they decided on a purchase that required approval
`report_purchase` | Report a completed purchase with the actual charged amount and a note; Sealgraf seals it into a receipt
`get_receipt` | Read a sealed receipt

## Resources

- [Sealgraf](https://sealgraf.com)
- [Protocol — IETF draft draft-gunuganti-agent-approval-evidence-00](https://datatracker.ietf.org/doc/draft-gunuganti-agent-approval-evidence/)
- Support: support@sealgraf.com
