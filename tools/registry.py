"""Central registry for available public-data tools."""

from langchain_core.tools import BaseTool

from tools.public_data.fewsnet import get_fewsnet_food_security
from tools.public_data.nasa_power import get_agroclimate_history
from tools.public_data.world_bank import get_world_bank_indicator

TOOL_REGISTRY: dict[str, BaseTool] = {
    tool.name: tool
    for tool in (
        get_fewsnet_food_security,
        get_agroclimate_history,
        get_world_bank_indicator,
    )
}


def get_tools_for_domain(domain: str | None = None) -> list[BaseTool]:
    """Return the registered tools relevant to a domain, or all tools."""
    domain_tools = {
        "agriculture": {
            "get_agroclimate_history",
            "get_fewsnet_food_security",
        },
        "research": {"get_world_bank_indicator"},
        "commerce": {"get_fewsnet_food_security"},
        "marketing": set(),
    }
    if domain is None:
        return list(TOOL_REGISTRY.values())
    if domain not in domain_tools:
        raise ValueError(f"Unsupported tool domain: {domain}")
    return [
        tool
        for name, tool in TOOL_REGISTRY.items()
        if name in domain_tools[domain]
    ]
