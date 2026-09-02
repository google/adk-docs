# Debug stdio connection issues
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
            # Add environment debugging
            env={'DEBUG': '1'}
        ),
    ),
)