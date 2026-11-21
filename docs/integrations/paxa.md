---
catalog_title: Paxa Labs
catalog_description: Generate Thai, English, and Mandarin speech, transcribe audio, and run OCR
catalog_icon: /integrations/assets/paxa.png
catalog_tags: ["mcp"]
---

# Paxa Labs MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [Paxa MCP Server](https://github.com/paxalabs/mcp) connects your ADK agent
to the [Paxa Labs](https://paxalabs.com/) speech and document API. This
integration gives your agent the ability to generate speech in Thai, English,
and Mandarin Chinese, transcribe recordings, read documents with OCR, and
translate text into Thai using natural language.

## Use cases

- **Multilingual speech**: Generate speech from 50 voices on Paxa TTS Flash v2.
  Every voice speaks Thai, English, and Mandarin Chinese, including sentences
  that mix them. Direction tags written into the text, such as `[whispering]`
  or `[laughs]`, set the delivery.

- **Voice design**: Describe a new voice in words, refine it, and save it to
  your account under its own id.

- **Voiceovers with captions**: Save speech to mp3, opus, or wav files, with
  matching srt or vtt subtitles timed from the spoken words.

- **Transcription**: Turn Thai, English, or mixed recordings and videos into
  text, with optional speaker labels, word timings, and subtitles.
  Transcription is in research preview.

- **Document reading**: Read PDFs and images, such as receipts, tax invoices,
  and forms, into Markdown, or fill a schema of typed fields from them.

- **Translation into Thai**: Translate text from other languages into Thai,
  with formality and glossary controls.

## Prerequisites

- Install [Node.js](https://nodejs.org/) 20 or later, which runs the server
  through `npx`
- Sign in to [Paxa Labs](https://paxalabs.com/sign-in) to create an account
- Create an [API key](https://paxalabs.com/app/keys) in the dashboard

## Use with agent

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        PAXA_API_KEY = "YOUR_PAXA_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="paxa_agent",
            instruction="Help users create speech, transcribe audio, and read documents",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@paxalabs/mcp",
                            ],
                            env={
                                "PAXA_API_KEY": PAXA_API_KEY,
                                # "PAXA_OUTPUT_DIR": "/path/to/output",  # Optional
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

        const PAXA_API_KEY = "YOUR_PAXA_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "paxa_agent",
            instruction: "Help users create speech, transcribe audio, and read documents",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@paxalabs/mcp"],
                        env: {
                            PAXA_API_KEY: PAXA_API_KEY,
                            // PAXA_OUTPUT_DIR: "/path/to/output",  // Optional
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## Available tools

### Speech

Tool | Description
---- | -----------
`text_to_speech` | Synthesize speech to an mp3, opus, or wav file, with optional srt or vtt subtitles
`list_voices` | List your designed voices, then the available voices with character notes
`speak` | Synthesize a short line and play it through the speakers
`queue_speech` | Read long content aloud through a playback queue
`control_playback` | Check, pause, resume, skip, or clear the playback queue
`play_audio` | Play a local audio file through the speakers

### Voice design

Tool | Description
---- | -----------
`design_voice` | Make a new voice from a written description and play the line it speaks
`refine_voice` | Change a draft voice in words and play its new line
`save_voice` | Save a draft as one of your voices, with an id the speech tools accept
`rename_voice` | Rename one of your designed voices
`delete_voice` | Delete one of your designed voices and free its slot

### Transcription

Tool | Description
---- | -----------
`transcribe_audio` | Transcribe a local recording or video, with optional speaker labels, word timings, and subtitles
`listen` | Record one spoken turn from the microphone and return its transcript

### Documents and translation

Tool | Description
---- | -----------
`ocr_document` | Read a local PDF or image into Markdown or structured blocks
`extract_fields` | Fill a schema of typed fields from a local PDF or image
`translate_to_thai` | Translate text from any language into Thai

### Account

Tool | Description
---- | -----------
`list_models` | List the available models, limits, and pricing
`get_account` | Check the credit balance, plan, and rate limits
`send_feedback` | Rate an output or report a problem, tied to request ids

The playback tools and the `listen` tool use the speakers and microphone of the
machine that runs the server. See
[Playback support](https://github.com/paxalabs/mcp#playback-support) for the
players and recorders each platform needs. Transcribing video and joining long
scripts into one audio file need [ffmpeg](https://ffmpeg.org/).

## Configuration

The Paxa MCP server can be configured using environment variables:

Variable | Description | Default
-------- | ----------- | -------
`PAXA_API_KEY` | Your Paxa Labs API key | Required
`PAXA_OUTPUT_DIR` | Directory where `text_to_speech` saves files | Working directory
`PAXA_DEFAULT_VOICE` | Voice used when a tool call does not pick one | `foithong`
`PAXA_TTS_MODEL` | Speech model used when a tool call does not pick one | `paxa-tts-flash-v2`
`PAXA_DEFAULT_SPEED` | Speaking rate from 0.5 to 1.5 | `1`

## Additional resources

- [Paxa MCP Server Repository](https://github.com/paxalabs/mcp)
- [Paxa MCP Server Documentation](https://paxalabs.com/docs/mcp)
- [Paxa Labs API Documentation](https://paxalabs.com/docs)
