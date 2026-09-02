# Test remote MCP connectivity
import aiohttp

async def test_mcp_connection():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://your-mcp-server.com/health') as resp:
            print(f"MCP Server Health: {resp.status}")