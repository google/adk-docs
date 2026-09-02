import java.util.Map;
import com.google.adk.tools.mcp.StreamableHttpServerParameters;
import com.google.adk.tools.mcp.McpToolset;

// Your ADK agent connects to the remote MCP service via Streamable HTTP
StreamableHttpServerParameters streamableParams = StreamableHttpServerParameters.builder()
        .url("https://your-mcp-server-url.run.app/mcp")
        .headers(Map.of("Authorization", "Bearer your-auth-token"))
        .build();

McpToolset toolset = new McpToolset(streamableParams);