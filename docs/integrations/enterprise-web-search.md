---
catalog_title: Enterprise Web Search
catalog_description: Ground ADK agents with policy-compliant web search results
catalog_icon: /integrations/assets/enterprise-web-search.png
catalog_tags: ["google", "search"]
---

# Enterprise Web Search tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The Enterprise Web Search tool grounds ADK agents with information from the
web while maintaining enterprise compliance and source control. Designed for
enterprise-grade workloads, this tool ensures grounding data aligns with
organizational security and compliance policies.

!!! note "Enterprise Web Search vs. Agent Platform Search"
    
    Enterprise Web Search is distinct from Agent Platform Search. While the Agent Platform
    Search queries indexed private data stores, Enterprise Web Search
    retrieves compliant public web data.

## Use cases

- **Enterprise Grounding**: Provide up-to-date web information to agents while
  maintaining organizational compliance standards.
- **Controlled Web Access**: Ensure agents query trusted web sources for
  research, market intelligence, or customer support tasks.
- **Regulated Workflows**: Deploy grounding capabilities in environments
  requiring strict auditability and data governance.

## Prerequisites

- Access to Google Cloud Platform with Agent Platform enabled.
- Configured GCP project with necessary permissions for Gemini models.
- The `google-adk` package (Python) or `@google/adk` package (TypeScript) installed:

=== "Python"

    ```bash
    pip install google-adk
    ```

=== "TypeScript"

    ```bash
    npm install @google/adk
    ```

## Use with ADK

The following example demonstrates how to configure an ADK agent with the
pre-instantiated `enterprise_web_search` tool:

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import enterprise_web_search

    root_agent = Agent(
        model="gemini-flash-latest",
        name="enterprise_search_agent",
        instruction="Answer user questions accurately using enterprise-compliant web search results.",
        tools=[enterprise_web_search],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, ENTERPRISE_WEB_SEARCH } from "@google/adk";

    const rootAgent = new LlmAgent({
      model: "gemini-flash-latest",
      name: "enterprise_search_agent",
      instruction: "Answer user questions accurately using enterprise-compliant web search results.",
      tools: [ENTERPRISE_WEB_SEARCH],
    });

    export { rootAgent };
    ```

Alternatively, instantiate the `EnterpriseWebSearchTool` class directly in Python:

```python
from google.adk.agents import Agent
from google.adk.tools.enterprise_search_tool import EnterpriseWebSearchTool

root_agent = Agent(
    model="gemini-flash-latest",
    name="enterprise_search_agent",
    instruction="Answer user questions accurately using enterprise-compliant web search results.",
    tools=[EnterpriseWebSearchTool()],
)
```

## Selection guidance

- Use standard Google Search for general-purpose applications requiring broad
  web coverage across any Gemini model.
- Use Enterprise Web Search when building enterprise agents that mandate
  compliance control, source auditing, and deployment on Gemini 2+ models.

## Additional resources

- [Agent Platform Web Grounding Overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/web-grounding-enterprise)
