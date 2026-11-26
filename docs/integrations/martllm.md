---
catalog_title: MartLLM
catalog_description: Generate images, videos, and music across many models with one key
catalog_icon: /integrations/assets/martllm.png
catalog_tags: ["mcp"]
---

# MartLLM MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [MartLLM MCP server](https://martllm.com/docs/mcp) connects your ADK agent
to [MartLLM](https://martllm.com), an API that serves image, video, music, and
speech models from many vendors behind one API key. The server exposes tools to
list models and their prices, price a request before running it, generate and
edit images, start video and music jobs, and wait for their results.

The server is hosted at `https://api.martllm.com/mcp` over streamable HTTP, so
no local install is required. The agent connects to the remote endpoint
directly.

## Use cases

- **Generate and edit images**: Create pictures from a prompt or change an
  existing picture with an editing model, and get back links to the results.

- **Make videos and music**: Start a video, music, or sound effect job and let
  the agent wait for it to finish before returning the file links.

- **Choose a model by price**: List the image, video, or music models available
  right now with their prices, and read the options each model accepts.

- **Control spend**: Price a request with `quote` before running it, and pass
  `max_cost` so a request that could cost more is refused before anything is
  spent.

## Prerequisites

- A working [ADK installation](/get-started/installation/)
- A MartLLM API key: sign up at [martllm.com](https://martllm.com/signup) and
  create a key in the dashboard. Tool calls that make something are billed to
  your prepaid MartLLM balance at the same price as the API.

## Use with agent

The agent connects to the hosted MartLLM MCP server over streamable HTTP and
authenticates with your API key in the `Authorization` header.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    MARTLLM_API_KEY = "YOUR_MARTLLM_API_KEY"

    root_agent = Agent(
        model="gemini-flash-latest",
        name="martllm_agent",
        instruction=(
            "You make images, videos, and music with the MartLLM tools. "
            "Use list_models and get_model to pick a model, quote a request "
            "before you run it, and use wait_job until a video or music job "
            "is done."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://api.martllm.com/mcp",
                    headers={"Authorization": f"Bearer {MARTLLM_API_KEY}"},
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const MARTLLM_API_KEY = "YOUR_MARTLLM_API_KEY";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "martllm_agent",
        instruction:
            "You make images, videos, and music with the MartLLM tools. " +
            "Use list_models and get_model to pick a model, quote a request " +
            "before you run it, and use wait_job until a video or music job " +
            "is done.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://api.martllm.com/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            Authorization: `Bearer ${MARTLLM_API_KEY}`,
                        },
                    },
                },
            }),
        ],
    });

    export { rootAgent };
    ```

## Configuration

To let an agent look up models and prices without an API key, point the
toolset at `https://api.martllm.com/mcp/public` and omit the `Authorization`
header. That endpoint exposes only the read-only `list_models`, `get_model`,
and `quote` tools, so it cannot make anything or spend money.

To keep an agent away from tools that spend from your balance, pass a
`tool_filter` with the tool names it may use, for example
`tool_filter=["list_models", "get_model", "quote", "balance"]`.

## Available tools

Tool | Description
---- | -----------
`list_models` | List the models you can call now with their price, filtered by type (chat, image, video, music, speech, transcription) or by name
`get_model` | Get one model's price and a JSON Schema of the options its requests take
`quote` | Price an image, video, music, or text-to-speech request without making anything
`generate_image` | Make pictures from a prompt and return links and the cost
`edit_image` | Change a picture (an `https://` link or `data:` URI) following a prompt, with an editing model
`start_video` | Start a video job and return its job ID
`start_music` | Start a music or sound effect job and return its job ID
`get_job` | Get a video or music job's status, progress, and file links once it succeeded
`wait_job` | Wait up to 50 seconds for a video or music job to end
`list_kits` | List your brand kits (reference pictures, style notes, and a voice) to reuse across models
`list_library` | List the files kept in your library, newest first
`balance` | Show what you can spend now and what is held for running requests

## Additional resources

- [MartLLM MCP server documentation](https://martllm.com/docs/mcp)
- [MartLLM API quickstart](https://martllm.com/docs/quickstart)
- [MartLLM models and prices](https://martllm.com/models)
- [MartLLM homepage](https://martllm.com)
