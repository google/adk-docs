---
catalog_title: LangChain Tool
catalog_description: Wrap and reuse third-party tools and schemas inside ADK agents
catalog_icon: /integrations/assets/toolbox.svg
catalog_tags: ["connectors"]
---

# LangChain tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

In Agent Development Kit (ADK) Python and ADK TypeScript, the `LangchainTool` wrapper adapts [LangChain](https://docs.langchain.com/) tools and LangChain-compatible tool objects so your ADK agents can call them directly. Instead of rewriting existing tool definitions, you wrap a tool instance and register it in your agent's `tools` list. The adapter translates parameter schemas into model-compatible function declarations, preserves tool metadata, and forwards arguments during execution.

## Use cases

- **Reuse existing LangChain tools**: Bring prebuilt and custom LangChain tools into ADK agents without rewriting execution logic or parameter schemas.
- **Structured parameter validation**: Wrap structured tools backed by Pydantic models, Zod schemas, or JSON Schema definitions so the model receives typed argument declarations.
- **Direct tool responses**: Return raw tool output directly to the caller without an extra model summarization step when a wrapped tool in ADK Python sets `return_direct=True`.

## Prerequisites

- Python 3.11 or later for ADK Python, or Node.js 20.19 or later for ADK
  TypeScript.
- An ADK project configured with model credentials, such as a Gemini API key set
  in `GOOGLE_API_KEY`.
- Any API keys or additional dependencies required by the specific LangChain
  tool you wrap.

## Installation

=== "Python"

    Install ADK and `langchain-core`, plus any community tool packages you need,
    such as `langchain-community`:

    ```bash
    pip install google-adk langchain-core
    ```

=== "TypeScript"

    Install the ADK core package, the integrations package, `@langchain/core`,
    and `zod`:

    ```bash
    npm install @google/adk @google/adk-integrations @langchain/core zod
    ```

## Use with agent

Wrap a LangChain tool with `LangchainTool` and pass it to your agent's `tools`
list:

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.integrations.langchain import LangchainTool
    from langchain_core.tools import tool


    @tool
    def calculate_order_total(unit_price: float, quantity: int) -> float:
        """Calculate the total price for an order."""
        return unit_price * quantity


    adk_order_tool = LangchainTool(tool=calculate_order_total)

    root_agent = Agent(
        model="gemini-flash-latest",
        name="langchain_tool_agent",
        instruction="Help users calculate order totals using the available tool.",
        tools=[adk_order_tool],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent } from "@google/adk";
    import { LangchainTool } from "@google/adk-integrations";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";

    const calculateOrderTotal = tool(
        async ({ unitPrice, quantity }) => unitPrice * quantity,
        {
            name: "calculate_order_total",
            description: "Calculate the total price for an order.",
            schema: z.object({
                unitPrice: z.number().describe("Price per unit"),
                quantity: z.number().int().describe("Number of units"),
            }),
        },
    );

    const adkOrderTool = new LangchainTool(calculateOrderTotal);

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "langchain_tool_agent",
        instruction: "Help users calculate order totals using the available tool.",
        tools: [adkOrderTool],
    });

    export { rootAgent };
    ```

## Available tools

This integration wraps any LangChain tool you provide rather than exposing a
fixed catalog of endpoints. In ADK Python, wrap any
`langchain_core.tools.BaseTool` instance, including `StructuredTool` and
`@tool`-decorated functions, or any object implementing a `run` or `_run`
method. In ADK TypeScript, wrap any object that satisfies the
`LangchainToolLike` type, including tools created with `@langchain/core/tools`.

The integration exports the following classes, functions, and types:

Symbol | Language | Description
------ | -------- | -----------
`LangchainTool`{ style="white-space: nowrap" } | Python, TypeScript | Wraps a LangChain tool as an ADK `FunctionTool`, translating its schema and forwarding calls.
`LangchainToolConfig`{ style="white-space: nowrap" } | Python, TypeScript | Configuration schema for creating a `LangchainTool` from an Agent Config file in ADK Python or from constructor options in ADK TypeScript.
`isLangchainTool`{ style="white-space: nowrap" } | TypeScript | Type guard that checks whether an object is an instance of `LangchainTool`.
`LangchainToolLike`{ style="white-space: nowrap" } | TypeScript | Structural type for a LangChain-compatible tool object with optional `name`, `description`, `argsSchema`, `schema`, `args`, and a runner method: `invoke`, `call`, `run`, `func`, `_run`, or `_call`.
`LangchainSchemaLike`{ style="white-space: nowrap" } | TypeScript | Accepted parameter schema types: ADK `SchemaLike` such as Zod schemas, objects with `toJsonSchema()`, `jsonSchema()`, or `modelJsonSchema()`, or plain JSON Schema objects.

## Configuration

### Constructor and config options

Override the wrapped tool's name and description when creating a
`LangchainTool`:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `tool` | Yes | None | LangChain tool instance to wrap, or its fully qualified import path in ADK Python Agent Config files. |
| `name` | No | `tool.name`{ style="white-space: nowrap" } | Custom tool name exposed to the model. Falls back to the wrapped function's name (or `"langchain_tool"` in TypeScript) when absent. |
| `description`{ style="white-space: nowrap" } | No | `tool.description`{ style="white-space: nowrap" } | Custom tool description exposed to the model. Falls back to the wrapped function's docstring in Python, or `""` if absent. |

In ADK Python Agent Config files, `LangchainToolConfig` defaults omitted `name`
and `description` fields to `""` and overrides the wrapped tool's metadata, so
specify both fields explicitly in YAML.

### Structured schemas and execution behavior

During tool declaration and execution, `LangchainTool` adapts LangChain schemas
and execution conventions to ADK:

=== "Python"

    - **Structured tools and async functions**: Wrap `StructuredTool` instances
      with a synchronous `func` or an asynchronous `coroutine` and a Pydantic
      `args_schema`. ADK builds the model function declaration from
      `args_schema` and ignores LangChain's internal `run_manager` parameter.
    - **Direct returns**: When a wrapped tool sets `return_direct=True`, ADK
      sets `tool_context.actions.skip_summarization = True` after a successful
      call so the raw result returns directly. If the tool returns an error
      dictionary with a truthy `"error"` key, such as a missing-argument error,
      ADK keeps summarization enabled so the model can observe the error and
      retry.
    - **Canonical import path**: Import `LangchainTool` from
      `google.adk.integrations.langchain`. The older
      `google.adk.tools.langchain_tool` path is deprecated.

    ```python
    from google.adk.integrations.langchain import LangchainTool
    from langchain_core.tools.structured import StructuredTool
    from pydantic import BaseModel, Field


    class AddInput(BaseModel):
        x: int = Field(..., description="First integer")
        y: int = Field(..., description="Second integer")


    async def add_numbers(x: int, y: int) -> int:
        return x + y


    structured_tool = StructuredTool.from_function(
        coroutine=add_numbers,
        name="add_numbers",
        description="Adds two integers together.",
        args_schema=AddInput,
    )

    adk_add_tool = LangchainTool(
        tool=structured_tool,
        name="sum_two_integers",
        description="Compute the sum of two integers.",
    )
    ```

=== "TypeScript"

    - **Constructor forms**: Construct `LangchainTool` with either a tool
      instance and an optional overrides object,
      `new LangchainTool(tool, { name, description })`, or a single
      `LangchainToolConfig` object,
      `new LangchainTool({ tool, name, description })`.
    - **Runner resolution**: ADK resolves the tool's execution method in order:
      `invoke`, `call`, `run`, `func`, `_run`, then `_call`. Prefer public
      entrypoints such as `invoke` or `call` when available so LangChain
      validates inputs once.
    - **Schema sources**: ADK extracts parameter definitions from `tool.args`,
      `tool.argsSchema`, or `tool.schema`, supporting Zod schemas, objects with
      `toJsonSchema()`, `jsonSchema()`, or `modelJsonSchema()`, and plain JSON
      Schema objects.
    - **Context forwarding**: ADK passes the optional ADK `Context` as the
      second argument when calling `invoke`, `call`, `run`, `_run`, or `_call`.
      When wrapping a `func`-only `DynamicTool`, ADK passes only the arguments
      object.

    ```typescript
    import type { Context } from "@google/adk";
    import { LangchainTool } from "@google/adk-integrations";
    import { z } from "zod";

    const sessionLookupTool = new LangchainTool({
        name: "lookup_session_note",
        description: "Look up a note scoped to the current session.",
        tool: {
            argsSchema: z.object({
                key: z.string().describe("Note key to look up"),
            }),
            _run: (args: Record<string, unknown>, toolContext?: Context) => {
                const sessionId = toolContext?.sessionId ?? "unknown";
                return `Fetched '${String(args.key)}' for session ${sessionId}`;
            },
        },
    });
    ```

### Load from Agent Config

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

Load a `LangchainTool` from an [Agent Config](/agents/config/) YAML file using
`LangchainTool.from_config` and `LangchainToolConfig`. Set `tool` to the fully
qualified Python import path of an existing LangChain tool instance, and specify
`name` and `description` explicitly so ADK does not overwrite them with empty
strings:

```yaml
tools:
  - name: google.adk.integrations.langchain.LangchainTool
    args:
      tool: my_package.my_tools.calculate_order_total
      name: calculate_order_total
      description: Calculate the total price for an order.
```

## Limitations

- **Required execution method**: In ADK Python, the wrapped object must define a
  `run` or `_run` method, and a `StructuredTool` must define `func`,
  `coroutine`, or a subclass `_run` override, or initialization raises
  `ValueError`. In ADK TypeScript, the wrapped object must define `invoke`,
  `call`, `run`, `func`, `_run`, or `_call`, or initialization throws
  `TypeError`.
- **LangChain runtime-injected parameters**: LangChain tools that rely on
  LangGraph-specific runtime injection, such as `ToolRuntime` or `Command` state
  updates, require a LangGraph execution runtime, and `LangchainTool` does not
  populate those parameters automatically.

## Additional resources

- [ADK Custom Tools](/tools-custom/)
- [LangChain StructuredTool sample (Python)](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/langchain_structured_tool_agent)
- [LangChain YouTube search sample (Python)](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/langchain_youtube_search_agent)
- [LangChain Tools Documentation (Python)](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain Tools Documentation (JavaScript/TypeScript)](https://docs.langchain.com/oss/javascript/langchain/tools)
- [google-adk on PyPI](https://pypi.org/project/google-adk/)
- [@google/adk-integrations on npm](https://www.npmjs.com/package/@google/adk-integrations)
