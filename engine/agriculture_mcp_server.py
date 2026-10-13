"""Backward-compatible import for the agriculture MCP server."""

from tools.mcp.agriculture_server import mcp

__all__ = ["mcp"]

if __name__ == "__main__":
    mcp.run(transport="http")
