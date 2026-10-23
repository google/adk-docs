# Enterprise Web Search tool for ADK

Supported in ADKPython v1.9.0TypeScript v1.5.0

The Google Cloud [Enterprise Web Search](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/Shared.Types/EnterpriseWebSearch) grounds ADK agents with information from the web while maintaining enterprise compliance and source control. Designed for enterprise-grade workloads, this tool ensures grounding data aligns with organizational security and compliance policies.

Enterprise Web Search vs. Agent Search

Enterprise Web Search is distinct from [Agent Search](https://adk.dev/integrations/agent-search/). While the Agent Search queries indexed private data stores, Enterprise Web Search retrieves compliant public web data.

Service Specific Terms

When using the Enterprise Web Search tool, you are obligated to comply with Google's Service Specific Terms, which include properly displaying search suggestions and required Google logos in your UI.

## Use cases

- **Enterprise Grounding**: Provide up-to-date web information to agents while maintaining organizational compliance standards.
- **Controlled Web Access**: Ensure agents query trusted web sources for research, market intelligence, or customer support tasks.
- **Regulated Workflows**: Deploy grounding capabilities in environments requiring strict auditability and data governance.

## Prerequisites

- Access to Google Cloud Platform with Agent Search enabled.
- Configured GCP project with necessary permissions for Gemini models.
- The environment variable `GOOGLE_GENAI_USE_ENTERPRISE=TRUE` must be set.
- The `google-adk` package (Python) or `@google/adk` package (TypeScript) installed:

```bash
pip install google-adk
```

```bash
npm install @google/adk
```

## Use with agent

The following example demonstrates how to configure an ADK agent with the pre-instantiated `enterprise_web_search` tool:

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

## Selection guidance

- Use standard Google Search for general-purpose applications requiring broad web coverage across any Gemini model.
- Use Enterprise Web Search when building enterprise agents that mandate compliance control, source auditing, and deployment on Gemini 2+ models.

## Additional resources

- [Agent Search Web Grounding Overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/web-grounding-enterprise)
