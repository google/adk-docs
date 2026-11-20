---
catalog_title: GetYouTubeTranscript
catalog_description: Fetch YouTube transcripts in any caption language, search YouTube, and read channel and playlist data
catalog_icon: /integrations/assets/getyoutubetranscript.png
catalog_tags: ["mcp"]
---

# GetYouTubeTranscript MCP tool for ADK

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [GetYouTubeTranscript MCP server](https://github.com/tubeagentkit/youtube-mcp)
connects your ADK agent to [GetYouTubeTranscript](https://getyoutubetranscript.com/),
a YouTube data API. It exposes full video transcripts in any caption language a
video has (optionally timestamped or machine-translated), YouTube search, and
channel, playlist and video data as MCP tools your agent can call with natural
language such as "Summarize this talk" or "What did the speaker say about
pricing, with timestamps?".

The server is hosted at `https://getyoutubetranscript.com/api/mcp` over
streamable HTTP, so no local install is required — the agent connects to the
remote endpoint directly.

## Use cases

- **Summarize and quote videos**: Fetch a video's transcript, with timestamps
  when you need to cite a moment, so the agent can summarize, answer questions
  or pull exact quotes.

- **Research a topic across YouTube**: Search YouTube, then read the
  transcripts of the most relevant videos and compare what each one says.

- **Monitor a channel or playlist**: List a channel's latest uploads, Shorts,
  live streams, playlists or community posts, or every video in a playlist, and
  process new videos as they appear.

- **Work across languages**: List the caption languages a video has, fetch the
  one you need, or translate the transcript into another language.

## Prerequisites

- A working [ADK installation](/get-started/installation/)
- A GetYouTubeTranscript API key — create one at
  [getyoutubetranscript.com/developers](https://getyoutubetranscript.com/developers)
  (a new account gets 100 credits, no card required)

## Use with agent

The agent connects to the hosted GetYouTubeTranscript MCP server over streamable
HTTP and authenticates with your API key as a bearer token in the
`Authorization` header.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

    GETYOUTUBETRANSCRIPT_API_KEY = "YOUR_GETYOUTUBETRANSCRIPT_API_KEY"

    root_agent = Agent(
        model="gemini-flash-latest",
        name="youtube_agent",
        instruction=(
            "You are a YouTube research assistant. Use the GetYouTubeTranscript "
            "tools to fetch transcripts, search YouTube, and read channel and "
            "playlist data, and cite timestamps when you quote a video."
        ),
        tools=[
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url="https://getyoutubetranscript.com/api/mcp",
                    headers={"Authorization": f"Bearer {GETYOUTUBETRANSCRIPT_API_KEY}"},
                ),
            )
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, MCPToolset } from "@google/adk";

    const GETYOUTUBETRANSCRIPT_API_KEY = "YOUR_GETYOUTUBETRANSCRIPT_API_KEY";

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "youtube_agent",
        instruction:
            "You are a YouTube research assistant. Use the GetYouTubeTranscript " +
            "tools to fetch transcripts, search YouTube, and read channel and " +
            "playlist data, and cite timestamps when you quote a video.",
        tools: [
            new MCPToolset({
                type: "StreamableHTTPConnectionParams",
                url: "https://getyoutubetranscript.com/api/mcp",
                transportOptions: {
                    requestInit: {
                        headers: {
                            Authorization: `Bearer ${GETYOUTUBETRANSCRIPT_API_KEY}`,
                        },
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
`get_youtube_transcript` | Full transcript of a video, optionally with timestamps, in a chosen caption language, optionally machine-translated
`get_transcript_languages` | List the caption languages a video has
`search_youtube` | Search YouTube videos or channels
`get_channel_latest_videos` | A channel's details and latest uploads
`list_channel_videos` | Every video a channel has uploaded, including Shorts and live streams
`search_channel_videos` | Search within one channel's videos
`list_channel_playlists` | A channel's playlists
`list_channel_posts` | A channel's community posts
`get_channel_banner` | A channel's banner and avatar
`list_playlist_videos` | Every video in a playlist
`get_related_videos` | Videos YouTube suggests next to a video
`get_video_dislikes` | A video's estimated likes and dislikes
`get_credits` | Your remaining credit balance (free)

Most calls cost 1 credit; failed calls (no captions, a private or removed
video) and `get_credits` are free. Transcripts come from the captions a video
already has, so a video with captions turned off returns no transcript.

## Additional resources

- [GetYouTubeTranscript MCP server repository](https://github.com/tubeagentkit/youtube-mcp)
- [GetYouTubeTranscript API documentation](https://getyoutubetranscript.com/docs)
- [GetYouTubeTranscript homepage](https://getyoutubetranscript.com/)
- [Get a GetYouTubeTranscript API key](https://getyoutubetranscript.com/developers)
