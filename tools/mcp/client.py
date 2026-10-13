from langchain_mcp_adapters.client import MultiServerMCPClient

class ZimSignalMCPClientManager:
    @staticmethod
    async def build_workspace_tools(access_token: str):
        """
        Builds tenant-isolated LangChain tools connecting to Google Workspace 
        remote MCP servers using Streamable HTTP transport and dynamic OAuth headers.
        """
        client = MultiServerMCPClient({
            "gmail": {
                "transport": "http",
                "url": "https://gmailmcp.googleapis.com/mcp/v1",
                "headers": {"Authorization": f"Bearer {access_token}"},
            },
            "calendar": {
                "transport": "http",
                "url": "https://calendarmcp.googleapis.com/mcp/v1",
                "headers": {"Authorization": f"Bearer {access_token}"},
            },
        }, tool_name_prefix=True)
        
        # Retrieves dynamic tools with tenant isolation enforced
        tools = await client.get_tools()
        return tools