---
catalog_title: CrewAI
catalog_description: Wrap and reuse framework tools inside ADK agents
catalog_icon: /integrations/assets/toolbox.svg
catalog_tags: ["connectors"]
---

# CrewAI tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The `CrewaiTool` wrapper adapts [CrewAI](https://docs.crewai.com/) tools and CrewAI-compatible tool objects so your Agent Development Kit (ADK) agents can call them directly. Instead of rewriting existing tool definitions, you wrap a tool instance and register it in your agent's `tools` list. The wrapper translates parameter schemas into model-compatible function declarations, normalizes tool names, and forwards arguments and ADK context during execution.

## Use cases

- **Reuse existing tool implementations**: Bring CrewAI tools and CrewAI-compatible tool objects into ADK agents without rewriting parameter schemas.
- **Flexible dynamic arguments**: Run tools that accept dynamic keyword arguments while keeping framework-internal parameters separate.
- **Cross-framework interoperability**: Share tool definitions between CrewAI workflows and ADK agents without maintaining duplicate wrappers.

## Prerequisites

- An ADK project configured with model credentials, such as a Gemini API key set in `GOOGLE_API_KEY`.
- Python 3.11 or later for ADK Python, or Node.js 24.13.0 or later for ADK TypeScript.
- Any API keys or credentials required by the specific CrewAI tool you wrap.

## Installation

=== "Python"

    Install ADK with the `extensions` extra:

    ```bash
    pip install "google-adk[extensions]"
    ```

    !!! note "Python version note"

        The `extensions` extra installs `crewai[tools]` automatically on Python 3.11. On newer Python versions supported by CrewAI, install `google-adk` and `crewai`, plus `crewai-tools` if you use pre-built tools:

        ```bash
        pip install google-adk crewai crewai-tools
        ```

=== "TypeScript"

    Install the ADK core package, the integrations package, and `zod` for schema definitions:

    ```bash
    npm install @google/adk @google/adk-integrations zod
    ```

## Use with agent

Wrap a CrewAI tool with `CrewaiTool` and pass it to your agent's `tools` list.

=== "Python"

    ```python
    from crewai.tools import BaseTool
    from google.adk.agents import Agent
    from google.adk.integrations.crewai import CrewaiTool
    from pydantic import BaseModel, Field


    class SearchInput(BaseModel):
        query: str = Field(..., description="The search query string")
        limit: int | None = Field(None, description="Maximum number of results")


    class CustomSearchTool(BaseTool):
        name: str = "Custom Search"
        description: str = "Search for information with an optional result limit."
        args_schema: type[BaseModel] = SearchInput

        def _run(self, query: str, **kwargs) -> str:
            limit = kwargs.get("limit", 5)
            return f"Searching for '{query}' with limit {limit}"


    crewai_search_tool = CustomSearchTool()

    adk_search_tool = CrewaiTool(
        crewai_search_tool,
        name="search_with_filters",
        description="Search for information with an optional result limit.",
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="crewai_search_agent",
        instruction="Help users search for information using the search_with_filters tool.",
        tools=[adk_search_tool],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent } from "@google/adk";
    import { CrewaiTool } from "@google/adk-integrations";
    import { z } from "zod";

    const searchTool = new CrewaiTool({
        name: "search_with_filters",
        description: "Search for information with an optional result limit.",
        tool: {
            name: "Custom Search",
            description: "Search for information with an optional result limit.",
            argsSchema: z.object({
                query: z.string().describe("The search query string"),
                limit: z
                    .number()
                    .int()
                    .optional()
                    .describe("Maximum number of results"),
            }),
            run: ({ query, limit }: Record<string, unknown>) => {
                const maxResults = typeof limit === "number" ? limit : 5;
                return `Searching for '${String(query)}' with limit ${maxResults}`;
            },
        },
    });

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "crewai_search_agent",
        instruction:
            "Help users search for information using the search_with_filters tool.",
        tools: [searchTool],
    });

    export { rootAgent };
    ```

## Available tools

This integration wraps any CrewAI tool you provide rather than exposing a fixed catalog of endpoints. In Python, you can wrap any `crewai.tools.BaseTool` subclass, including pre-built tools from `crewai-tools`. In TypeScript, you can wrap any object that satisfies the `CrewaiToolLike` interface.

The integration exports the following classes, functions, and interfaces:

Symbol | Language | Description
------ | -------- | -----------
`CrewaiTool` | Python, TypeScript | Wraps a CrewAI tool as an ADK `FunctionTool`, translating its schema and forwarding calls.
`CrewaiToolConfig` | Python, TypeScript | Configuration schema for creating a `CrewaiTool` from an Agent Config file in ADK Python or from constructor options in ADK TypeScript.
`isCrewaiTool` | TypeScript | Type guard that checks whether an object is an instance of `CrewaiTool`.
`CrewaiToolLike` | TypeScript | Structural interface for a CrewAI-compatible tool object with `name`, `description`, `argsSchema`, and `run`.
`CrewaiSchemaLike` | TypeScript | Accepted parameter schema types: Zod schemas, objects with `jsonSchema()` or `modelJsonSchema()`, or plain JSON Schema objects.

## Configuration

### Constructor and config options

You can override the wrapped tool's name and description when creating a `CrewaiTool`.

Option | Required | Default | Description
------ | -------- | ------- | -----------
`tool` | Yes | None | The CrewAI tool instance to wrap. In ADK Python Agent Config files, specify the fully qualified import path to the tool instance.
`name` | Python constructor: Yes, may be `""`; Config & TypeScript: No | Normalized `tool.name` | Custom tool name exposed to the model. When empty or omitted, ADK converts `tool.name` to lowercase and replaces spaces with underscores, so `"Custom Search"` becomes `"custom_search"`. In ADK TypeScript, if `tool.name` is also absent, ADK falls back to `tool.run.name` or `"crewai_tool"`.
`description` | No | `tool.description` or `""` | Custom tool description exposed to the model. When empty or omitted, ADK uses the underlying tool's `description`.

### Parameter schemas, arguments, and context

During tool declaration and execution, `CrewaiTool` translates parameter schemas into model function declarations, forwards arguments, and passes ADK execution context when requested.

=== "Python"

    - **Schema translation**: Builds the model function declaration from the Pydantic model in `tool.args_schema`.
    - **Keyword arguments (`**kwargs`)**: When the wrapped callable accepts `**kwargs`, ADK forwards all model arguments while stripping framework-internal keys like `self`. When the callable declares explicit parameters without `**kwargs`, ADK filters out unexpected arguments.
    - **Context injection**: Declare a `tool_context` parameter, or any parameter annotated with `Context`, on the wrapped tool's `run` method to receive ADK's `Context`:

    ```python
    from crewai.tools import BaseTool
    from google.adk.agents.context import Context
    from google.adk.integrations.crewai import CrewaiTool
    from pydantic import BaseModel, Field


    class SessionSearchInput(BaseModel):
        query: str = Field(..., description="The search query string")


    class SessionSearchTool(BaseTool):
        name: str = "Session Search"
        description: str = "Search using the active session ID."
        args_schema: type[BaseModel] = SessionSearchInput

        def run(self, tool_context: Context, query: str, **kwargs) -> str:
            session_id = tool_context.session.id
            return f"Searching for '{query}' in session {session_id}"

        def _run(self, query: str, **kwargs) -> str:
            return f"Searching for '{query}'"


    context_aware_tool = CrewaiTool(
        SessionSearchTool(),
        name="session_search",
    )
    ```

=== "TypeScript"

    - **Schema translation**: Normalizes Zod schemas, objects exposing `jsonSchema()` or `modelJsonSchema()`, and plain JSON Schema objects (`CrewaiSchemaLike`).
    - **Constructor forms**: Construct `CrewaiTool` with either a single `CrewaiToolConfig` object (`new CrewaiTool({ tool, name, description })`) or a tool instance followed by an options object (`new CrewaiTool(tool, { name, description })`).
    - **Context injection**: Accept an optional `Context` second argument in the wrapped tool's `run` method:

    ```typescript
    import type { Context } from "@google/adk";
    import { CrewaiTool } from "@google/adk-integrations";
    import { z } from "zod";

    const contextAwareTool = new CrewaiTool({
        tool: {
            name: "Session Search",
            description: "Search using the active session ID.",
            argsSchema: z.object({
                query: z.string().describe("The search query string"),
            }),
            run: (args: Record<string, unknown>, toolContext?: Context) => {
                const query = String(args.query ?? "");
                const sessionId = toolContext?.sessionId ?? "unknown";
                return `Searching for '${query}' in session ${sessionId}`;
            },
        },
    });
    ```

### Loading from Agent Config (ADK Python)

In ADK Python, you can instantiate `CrewaiTool` from an [Agent Config](/agents/config/) YAML file using `CrewaiTool.from_config` and `CrewaiToolConfig`. Specify `tool` as the fully qualified Python path to an existing CrewAI tool instance:

```yaml
tools:
  - name: google.adk.integrations.crewai.CrewaiTool
    args:
      tool: my_package.my_tools.crewai_search_tool
      name: search_with_filters
      description: Search for information with an optional result limit.
```

## Additional resources

- [ADK Custom Tools](/tools-custom/)
- [CrewAI tool kwargs sample (Python)](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/crewai_tool_kwargs)
- [CrewAI Tools Documentation](https://docs.crewai.com/en/concepts/tools)
- [CrewAI on GitHub](https://github.com/crewAIInc/crewAI)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
- [@google/adk-integrations on npm](https://www.npmjs.com/package/@google/adk-integrations)
