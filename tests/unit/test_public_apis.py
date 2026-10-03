import pytest
from tools.definitions.world_bank import get_world_bank_indicator
from tools.definitions.nasa_power import get_agroclimate_history
from tools.definitions.fewsnet import get_fewsnet_food_security


@pytest.mark.asyncio
async def test_world_bank_tool_structure(httpx_mock):
    mock_payload = [
        {"page": 1, "total": 1},
        [{"date": "2024", "value": 27368627153.2}],
    ]
    httpx_mock.add_response(
        url="https://api.worldbank.org/v2/country/ZWE/indicator/NY.GDP.MKTP.CD?format=json&date=2020%3A2024&per_page=200",
        json=mock_payload,
    )

    res = await get_world_bank_indicator.ainvoke(
        {
            "country": "ZWE",
            "indicator": "NY.GDP.MKTP.CD",
            "start_year": 2020,
            "end_year": 2024,
        }
    )
    assert "country" in res
    assert "observations" in res
    assert res["country"] == "ZWE"


@pytest.mark.asyncio
async def test_nasa_power_tool_structure(httpx_mock):
    mock_payload = {
        "properties": {
            "parameter": {
                "PRECTOTCORR": {"20240101": 5.2},
                "T2M": {"20240101": 24.5},
            }
        }
    }
    httpx_mock.add_response(
        url="https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M%2CT2M_MAX%2CT2M_MIN%2CPRECTOTCORR%2CRH2M&community=AG&longitude=31.0&latitude=-17.8&start=20240101&end=20240101&format=JSON",
        json=mock_payload,
    )

    res = await get_agroclimate_history.ainvoke(
        {
            "latitude": -17.8,
            "longitude": 31.0,
            "start": "20240101",
            "end": "20240101",
        }
    )
    assert "daily_data" in res
    assert "PRECTOTCORR" in res["daily_data"]


@pytest.mark.asyncio
async def test_fewsnet_tool_structure(httpx_mock):
    mock_payload = [{"country_code": "ZW", "ipc_stage": 3}]
    httpx_mock.add_response(
        url="https://fews.net/api/v1/ipc?country=ZW",
        json=mock_payload,
    )

    res = await get_fewsnet_food_security.ainvoke({"country_code": "ZW"})
    assert "country" in res
    assert "data_points" in res
    assert res["country"] == "ZW"