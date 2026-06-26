import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# This describes HOW to start the server process so the client can talk to it.
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Ask the server: what tools do you have?
            tools_response = await session.list_tools()
            print("Available tools:")
            for tool in tools_response.tools:
                print(f" - {tool.name}: {tool.description}")

            # Now actually call one tool with real arguments
            result = await session.call_tool("lookup_billing_info", {"customer_id": "customer_002"})
            print("\nResult of calling lookup_billing_info:")
            print(result.content)

asyncio.run(main())