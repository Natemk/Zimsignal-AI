import httpx
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain.tools import tool


class FEWSNETOutput(BaseModel):
    country: str = Field(description="ISO country code")
    data_points: list[dict] = Field(description="Normalized food security observations")


@tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def get_fewsnet_food_security(country_code: str) -> dict:
    """Fetch food security IPC classification data from FEWS NET API."""
    url = f"https://fews.net/api/v1/ipc?country={country_code}"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url)
        response.raise_for_status()
        raw_data = response.json()

        # Normalize result into typed dictionary format
        normalized = FEWSNETOutput(
            country=country_code,
            data_points=raw_data if isinstance(raw_data, list) else [raw_data]
        )
        return normalized.model_dump()