import com.google.adk.kt.tools.mcp.McpConnectionParameters
import com.google.adk.kt.tools.mcp.McpToolset

// Your ADK agent connects to the remote MCP service via Streamable HTTP
// headerProvider is suspend, so fetchToken() can await a fresh token per request;
// it also disables session reuse, so use StreamableHttp(headers = ...) for a fixed one.
val toolset =
    McpToolset.McpToolsetConfig(
        streamableHttpConnectionParams =
            McpConnectionParameters.StreamableHttp(
                url = "https://your-mcp-server-url.run.app/mcp",
            ),
    ).toToolset(headerProvider = { mapOf("Authorization" to "Bearer ${fetchToken()}") })