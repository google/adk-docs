---
catalog_title: Parallel
catalog_description: Web search, extraction, and cited deep research for AI agents
catalog_icon: /integrations/assets/parallel.png
catalog_tags: ["search","mcp"]
---

# Parallel web research tools for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

The [`parallel-google-adk`](https://pypi.org/project/parallel-google-adk/) package connects your ADK agent to [Parallel](https://parallel.ai), a web research API purpose-built for AI agents. Unlike the built-in `google_search` tool (Gemini-only, one tool per agent), Parallel works with any model alongside other tools, and adds clean content extraction, structured enrichment, and long-running deep research with per-claim citations.

## Use cases

- **Research assistants**: Ground answers in cited current sources rather than the model's training data.

- **Market and competitive intelligence**: Pull structured facts about companies, people, or products with per-field citations.

- **Document processing pipelines**: Extract clean content from messy web pages and multi-page PDFs in batch.

- **Long-running deep research**: Spawn multi-hop investigations that return comprehensive cited reports — useful as a tool the agent calls and awaits.

## Prerequisites

- A [Parallel account](https://platform.parallel.ai)
- An [API key](https://platform.parallel.ai/settings/api-keys) from the Parallel platform

## Use with agent

=== "Package (recommended)"

    Install the package:

    ```bash
    uv add parallel-google-adk           # or: pip install parallel-google-adk
    export PARALLEL_API_KEY=your-key-here
    ```

    Pick the right tool by intent: quick fact lookup → `web_search`; you already have URLs → `web_fetch` or `extract`; comprehensive cited report → `deep_research`; structured enrichment over a list → `enrich`.

    ```python
    import asyncio

    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    from parallel_google_adk import (
        deep_research,
        enrich,
        extract,
        web_fetch,
        web_search,
    )

    root_agent = LlmAgent(
        model="gemini-flash-latest",
        name="research_agent",
        instruction=(
            "You are a research assistant. "
            "For quick fact lookups, call web_search. "
            "For specific URLs, call web_fetch or extract. "
            "For comprehensive cited reports, call deep_research. "
            "Always cite your sources."
        ),
        tools=[web_search, web_fetch, extract, deep_research, enrich],
    )


    async def main() -> None:
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name="parallel-demo", user_id="demo"
        )
        runner = Runner(
            agent=root_agent,
            app_name="parallel-demo",
            session_service=session_service,
        )

        user_message = types.Content(
            role="user",
            parts=[types.Part(text="What does Parallel's Search API do? Cite parallel.ai.")],
        )
        async for event in runner.run_async(
            user_id="demo", session_id=session.id, new_message=user_message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)


    asyncio.run(main())
    ```

=== "Remote MCP Server"

    The Parallel Search MCP exposes `web_search` and `web_fetch` only. For `extract`, `deep_research`, or `enrich`, use the package above. The [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp) plugs into ADK's `MCPToolset`:

    ```python
    import os

    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    PARALLEL_API_KEY = os.environ["PARALLEL_API_KEY"]

    root_agent = LlmAgent(
        model="gemini-flash-latest",
        name="research_agent",
        instruction="You are a research assistant. Always cite sources.",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://search.parallel.ai/mcp",
                    headers={"Authorization": f"Bearer {PARALLEL_API_KEY}"},
                ),
            ),
        ],
    )
    ```

## Available tools

Tool | Description
---- | -----------
`web_search` | Grounded web search. Takes a natural-language objective plus keyword queries, returns LLM-optimized excerpts with source URLs.
`web_fetch` | Clean content from a single URL. Handles JavaScript-rendered pages and PDFs.
`extract` | Batch extraction across 1–20 URLs with an optional focus objective.
`deep_research` | Multi-hop investigation with per-claim citations. Returns a comprehensive report. Configurable processor (`pro-fast`, `pro`, `ultra`).
`enrich` | Structured (JSON-Schema-conforming) enrichment of a list of entities, with per-field citations.

## Tracing plugin

`ParallelTracingPlugin` is an optional observability hook. It records latency, citation count, and (when reported) cost for every Parallel tool call onto the session state at `state["_parallel_calls"]`:

```python
from google.adk.runners import Runner
from parallel_google_adk import ParallelTracingPlugin

runner = Runner(
    agent=root_agent,
    app_name="my-app",
    session_service=session_service,
    plugins=[ParallelTracingPlugin()],
)
```

## Additional resources

- [`parallel-google-adk` on GitHub](https://github.com/parallel-web/parallel-google-adk)
- [`parallel-google-adk` on PyPI](https://pypi.org/project/parallel-google-adk/)
- [Parallel docs](https://docs.parallel.ai)
- [Search API quickstart](https://docs.parallel.ai/search-api/search-quickstart)
- [Task API quickstart](https://docs.parallel.ai/task-api/task-quickstart)
- [Extract API quickstart](https://docs.parallel.ai/extract-api/extract-quickstart)
- [Search MCP reference](https://docs.parallel.ai/integrations/mcp/search-mcp)
- [`parallel-web` Python SDK](https://github.com/parallel-web/parallel-sdk-python)
