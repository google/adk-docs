---
catalog_title: EmpirioLabs AI
catalog_description: Generate images, video, speech, and audio with hosted models
catalog_icon: /integrations/assets/empiriolabs.png
catalog_tags: ["mcp"]
---

# EmpirioLabs AI MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [EmpirioLabs AI MCP server](https://docs.empiriolabs.ai/mcp) connects your
ADK agent to [EmpirioLabs AI](https://empiriolabs.ai), specialized AI model
hosting for open, proprietary, and custom stacks. Your agent can search the
model catalog, then generate and edit images, video, speech, music, and 3D
models, transcribe audio, and read documents with the models it finds.

## Use cases

- **Generate media**: Create images, video, speech, music, and 3D models from a
  prompt, or edit an existing image with an instruction.
- **Choose a model for a task**: Search the catalog by modality and compare
  models by their prices and supported parameters.
- **Turn files into text**: Transcribe audio and video, and read PDFs and
  images as Markdown.
- **Track long-running work**: Start a video or another long generation, then
  check its status and collect the output with the job tools.

## Prerequisites

- Create an [EmpirioLabs AI API key](https://platform.empiriolabs.ai/dashboard/api-keys).
  Generation tools use credits from your EmpirioLabs AI account.

## Use with agent

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        EMPIRIOLABS_API_KEY = "YOUR_EMPIRIOLABS_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="empiriolabs_agent",
            instruction="Help users generate images, video, speech, and audio with EmpirioLabs AI models",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.empiriolabs.ai/mcp/media",
                        headers={
                            "Authorization": f"Bearer {EMPIRIOLABS_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const EMPIRIOLABS_API_KEY = "YOUR_EMPIRIOLABS_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "empiriolabs_agent",
            instruction: "Help users generate images, video, speech, and audio with EmpirioLabs AI models",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.empiriolabs.ai/mcp/media",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${EMPIRIOLABS_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Configuration

The URL path selects which tools the agent sees:

URL | Tools
--- | -----
`https://mcp.empiriolabs.ai/mcp/media` | Model catalog, media generation, jobs, and account usage
`https://mcp.empiriolabs.ai/mcp/inference` | Model catalog, chat, embeddings, reranking, web search, jobs, and account usage
`https://mcp.empiriolabs.ai/mcp` | Every toolset, including batch, GPU Cloud, and hosted agents

You can also combine toolsets with `+`, for example
`https://mcp.empiriolabs.ai/mcp/models+media+jobs`.

Generation tools return finished output links when the work completes within
about 40 seconds. Longer work, such as most videos, returns a `job_id` that the
agent passes to `get_job`. Output links are signed and expire, so download any
file you want to keep.

## Available tools

The `media` profile used above includes these tools:

Tool | Description
---- | -----------
`list_models` | List models with their author, modality, endpoints, and prices
`get_model` | Get one model's details, prices, and supported parameters
`generate_image` | Generate images from a prompt with an image model
`edit_image` | Edit an existing image with an instruction
`generate_video` | Generate a video from a prompt or an image
`text_to_speech` | Turn text into speech with a chosen voice
`list_voices` | List the voices available for text to speech
`generate_audio` | Generate music or sound effects from a prompt
`transcribe_audio` | Transcribe an audio or video file at a URL
`read_document` | Read a PDF or an image and return each page as Markdown
`analyze_image` | Answer a question about an image with a vision model
`generate_3d` | Generate a 3D model from an image
`compose_video` | Create a finished video with script, visuals, voice, and music
`get_job` | Check a generation job and return its output when it finishes
`list_jobs` | List recent generation jobs
`cancel_job` | Cancel a running generation job

## Additional resources

- [EmpirioLabs AI MCP server documentation](https://docs.empiriolabs.ai/mcp)
- [EmpirioLabs AI documentation](https://docs.empiriolabs.ai)
- [EmpirioLabs AI MCP server listing repository](https://github.com/EmpirioLabs-AI/mcp)
