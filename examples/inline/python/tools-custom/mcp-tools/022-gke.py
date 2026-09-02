# GKE-specific MCP configuration
# Use service discovery for MCP servers within the cluster
McpToolset(
    connection_params=SseConnectionParams(
        url="http://mcp-service.default.svc.cluster.local:8080/sse"
    ),
)