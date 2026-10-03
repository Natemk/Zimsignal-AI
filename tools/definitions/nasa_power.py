import httpx
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain.tools import tool


class AgroclimateNormalizedOutput(BaseModel):
    latitude: float
    longitude: float
    daily_data: dict = Field(description="Map of date to weather metrics")


@tool
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def get_agroclimate_history(
    latitude: float, longitude: float, start: str, end: str
) -> dict:
    """Fetch analysis-ready agroclimate history (temperature, precipitation, humidity) from NASA POWER."""
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": start,
        "end": end,
        "format": "JSON",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

        parameters = payload.get("properties", {}).get("parameter", {})
        normalized = AgroclimateNormalizedOutput(
            latitude=latitude,
            longitude=longitude,
            daily_data=parameters
        )
        return normalized.model_dump()