package com.google.adk.kt.examples.mcp

import com.google.adk.kt.agents.Instruction
import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.tools.mcp.McpConnectionParameters
import com.google.adk.kt.tools.mcp.McpToolset
import io.modelcontextprotocol.client.transport.ServerParameters
import java.time.Duration

// --8<-- [start:stdio_mcp]
/**
 * Creating an agent that uses a local filesystem MCP server via stdio.
 */
fun createStdioMcpAgent() {
    val fileSystemToolset =
        McpToolset.McpToolsetConfig(
            stdioConnectionParams =
                McpConnectionParameters.Stdio(
                    serverParameters =
                        ServerParameters.builder("npx")
                            .args(
                                listOf(
                                    "-y",
                                    "@modelcontextprotocol/server-filesystem",
                                    "/path/to/folder",
                                )
                            )
                            .build(),
                    timeoutDuration = Duration.ofSeconds(10),
                ),
        ).toToolset()

    val fileAgent =
        LlmAgent(
            name = "file_system_agent",
            model = Gemini(name = "gemini-flash-latest"),
            instruction = Instruction("Help the user manage their files."),
            toolsets = listOf(fileSystemToolset),
        )
}
// --8<-- [end:stdio_mcp]

// --8<-- [start:http_mcp]
/**
 * Creating an agent that uses a remote MCP server via Streamable HTTP.
 */
fun createHttpMcpAgent() {
    val mapsToolset =
        McpToolset.McpToolsetConfig(
            streamableHttpConnectionParams =
                McpConnectionParameters.StreamableHttp(
                    url = "https://mapstools.googleapis.com/mcp",
                    headers = mapOf("X-Goog-Api-Key" to "YOUR_API_KEY"),
                ),
        ).toToolset()

    val travelAgent =
        LlmAgent(
            name = "travel_planner_agent",
            model = Gemini(name = "gemini-flash-latest"),
            instruction = Instruction("A helpful assistant for planning travel routes."),
            toolsets = listOf(mapsToolset),
        )
}
// --8<-- [end:http_mcp]
