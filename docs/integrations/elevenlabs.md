---
catalog_title: ElevenLabs
catalog_description: Generate speech, clone voices, transcribe audio, and create sound effects
catalog_icon: /adk-docs/integrations/assets/elevenlabs.png
catalog_tags: ["mcp"]
---

# ElevenLabs MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp)
connects your ADK agent to the [ElevenLabs](https://elevenlabs.io/) AI audio
platform. This integration gives your agent the ability to generate speech,
clone voices, transcribe audio, create sound effects, and build conversational
AI experiences using natural language.


## Use cases

- **Text-to-Speech Generation**: Convert text into natural-sounding speech
  using a variety of voices, with fine-grained control over stability, style,
  and similarity settings.

- **Voice Cloning & Design**: Clone voices from audio samples or generate new
  voices from text descriptions of desired characteristics like age, gender,
  accent, and tone.

- **Audio Processing**: Isolate speech from background noise, convert audio to
  sound like different voices, or transcribe speech to text with speaker
  identification.

- **Sound Effects & Soundscapes**: Generate sound effects and ambient
  soundscapes from text descriptions, such as "a thunderstorm in a dense jungle
  with animals reacting to the weather."

## Prerequisites

- Sign up for an [ElevenLabs account](https://elevenlabs.io/app/sign-up)
- Generate an [API key](https://elevenlabs.io/app/settings/api-keys) from your
  account settings

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="elevenlabs_agent",
            instruction="Help users generate speech, clone voices, and process audio",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["elevenlabs-mcp"],
                            env={
                                "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
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

        const ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "elevenlabs_agent",
            instruction: "Help users generate speech, clone voices, and process audio",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["elevenlabs-mcp"],
                        env: {
                            ELEVENLABS_API_KEY: ELEVENLABS_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Text-to-speech and voice

Tool | Description
---- | -----------
`text_to_speech` | Generate speech from text using a specified voice
`speech_to_speech` | Transform audio to sound like a different voice
`text_to_voice` | Generate a voice preview from text description
`create_voice_from_preview` | Save a generated voice preview to your library
`voice_clone` | Clone a voice from audio samples
`get_voice` | Get details about a specific voice
`search_voices` | Search for voices in your library
`search_voice_library` | Search the public voice library
`list_models` | List available text-to-speech models

### Audio processing

Tool | Description
---- | -----------
`speech_to_text` | Transcribe audio to text with speaker identification
`text_to_sound_effects` | Generate sound effects from text descriptions
`isolate_audio` | Separate speech from background noise and music
`play_audio` | Play an audio file locally
`compose_music` | Generate music from a description
`create_composition_plan` | Create a plan for music composition

### Conversational AI

Tool | Description
---- | -----------
`create_agent` | Create a conversational AI agent
`get_agent` | Get details about a specific agent
`list_agents` | List all your conversational AI agents
`add_knowledge_base_to_agent` | Add a knowledge base to an agent
`make_outbound_call` | Initiate an outbound phone call using an agent
`list_phone_numbers` | List available phone numbers
`get_conversation` | Get details about a specific conversation
`list_conversations` | List all conversations

### Account

Tool | Description
---- | -----------
`check_subscription` | Check your subscription and credit usage

## Configuration

The ElevenLabs MCP server can be configured using environment variables:

Variable | Description | Default
-------- | ----------- | -------
`ELEVENLABS_API_KEY` | Your ElevenLabs API key | Required
`ELEVENLABS_MCP_BASE_PATH` | Base path for file operations | `~/Desktop`
`ELEVENLABS_MCP_OUTPUT_MODE` | How generated files are returned | `files`
`ELEVENLABS_API_RESIDENCY` | Data residency region (enterprise only) | `us`

### Output modes

The `ELEVENLABS_MCP_OUTPUT_MODE` environment variable supports three modes:

- **`files`** (default): Save files to disk and return file paths
- **`resources`**: Return files as MCP resources (base64-encoded binary data)
- **`both`**: Save files to disk AND return as MCP resources

## Additional resources

- [ElevenLabs MCP Server Repository](https://github.com/elevenlabs/elevenlabs-mcp)
- [Introducing ElevenLabs MCP](https://elevenlabs.io/blog/introducing-elevenlabs-mcp)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)
