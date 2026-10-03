import httpx
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain.tools import tool


class IndicatorObservation(BaseModel):
    year: str
    value: float | None


class WorldBankNormalizedOutput(BaseModel):
    country: str
    indicator: str
    observations: list[IndicatorObservation]


@tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def get_world_bank_indicator(
    country: str, indicator: str, start_year: int, end_year: int
) -> dict:
    """Return World Bank indicator observations for a country and year range."""
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 200,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        payload = r.json()

        raw_obs = payload[1] if len(payload) > 1 and payload[1] else []
        normalized_list = [
            IndicatorObservation(
                year=item.get("date", ""),
                value=item.get("value")
            )
            for item in raw_obs
        ]

        normalized = WorldBankNormalizedOutput(
            country=country,
            indicator=indicator,
            observations=normalized_list
        )
        return normalized.model_dump()