---
catalog_title: Cartesia
catalog_description: Generate speech, localize voices, and create audio content
catalog_icon: /adk-docs/integrations/assets/cartesia.png
catalog_tags: ["mcp"]
---

# Cartesia MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Cartesia MCP Server](https://github.com/cartesia-ai/cartesia-mcp) connects
your ADK agent to the [Cartesia](https://cartesia.ai/) AI audio platform. This
integration gives your agent the ability to generate speech, localize voices
across languages, and create audio content using natural language.

## Use cases

- **Text-to-Speech Generation**: Convert text into natural-sounding speech
  using Cartesia's diverse voice library, with control over voice selection and
  output format.

- **Voice Localization**: Transform existing voices into different languages
  while preserving the original speaker's characteristics—ideal for
  multilingual content creation.

- **Audio Infill**: Fill gaps between audio segments to create smooth
  transitions, useful for podcast editing or audiobook production.

- **Voice Transformation**: Convert audio clips to sound like different voices
  from Cartesia's library.

## Prerequisites

- Sign up for a [Cartesia account](https://play.cartesia.ai/sign-in)
- Generate an [API key](https://play.cartesia.ai/keys) from the Cartesia
  playground

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="cartesia_agent",
            instruction="Help users generate speech and work with audio content",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["cartesia-mcp"],
                            env={
                                "CARTESIA_API_KEY": CARTESIA_API_KEY,
                                # "OUTPUT_DIRECTORY": "/path/to/output",  # Optional
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "cartesia_agent",
            instruction: "Help users generate speech and work with audio content",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["cartesia-mcp"],
                        env: {
                            CARTESIA_API_KEY: CARTESIA_API_KEY,
                            // OUTPUT_DIRECTORY: "/path/to/output",  // Optional
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
`text_to_speech` | Convert text to audio using a specified voice
`list_voices` | List all available Cartesia voices
`get_voice` | Get details about a specific voice
`clone_voice` | Clone a voice from audio samples
`update_voice` | Update an existing voice
`delete_voice` | Delete a voice from your library
`localize_voice` | Transform a voice into a different language
`voice_change` | Convert an audio file to use a different voice
`infill` | Fill gaps between audio segments

## Configuration

The Cartesia MCP server can be configured using environment variables:

Variable | Description | Required
-------- | ----------- | --------
`CARTESIA_API_KEY` | Your Cartesia API key | Yes
`OUTPUT_DIRECTORY` | Directory to store generated audio files | No

## Additional resources

- [Cartesia MCP Server Repository](https://github.com/cartesia-ai/cartesia-mcp)
- [Cartesia MCP Documentation](https://docs.cartesia.ai/integrations/mcp)
- [Cartesia Playground](https://play.cartesia.ai/)
