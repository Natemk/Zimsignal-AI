from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server for ZimSignal Agriculture
mcp = FastMCP("ZimSignal Agriculture")

@mcp.tool()
async def get_latest_market_signal(commodity: str, province: str | None = None) -> dict:
    """Return recent normalized, sourced market signals for agriculture commodities."""
    # Simulated database or trusted API response
    return {
        "commodity": commodity,
        "province": province or "National",
        "price_trend": "bullish",
        "average_price_usd": 320.50,
        "source": "ZimSignal Market Intelligence"
    }

@mcp.tool()
async def search_marketplace(commodity: str, province: str | None = None) -> list[dict]:
    """Search active marketplace listings and buyer demand."""
    return [
        {
            "listing_id": "lst_991",
            "commodity": commodity,
            "province": province or "Harare",
            "volume_tons": 50,
            "buyer_type": "Agro-Processor"
        }
    ]

if __name__ == "__main__":
    # Run using network transport (HTTP/SSE) suitable for web services
    mcp.run(transport="http")