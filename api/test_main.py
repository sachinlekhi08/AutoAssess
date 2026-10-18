import httpx
import pytest

from api.main import app


SAMPLES = [
    {"buying": "vhigh", "maint": "vhigh", "doors": "2", "persons": "2", "lug_boot": "small", "safety": "low"},
    {"buying": "low", "maint": "low", "doors": "4", "persons": "more", "lug_boot": "big", "safety": "high"},
    {"buying": "med", "maint": "med", "doors": "4", "persons": "4", "lug_boot": "med", "safety": "high"},
]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client


@pytest.mark.anyio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["model_ready"] is True


@pytest.mark.anyio
@pytest.mark.parametrize("data", SAMPLES)
async def test_prediction_samples(client, data):
    response = await client.post("/predict", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["prediction"] in ["Unacceptable", "Acceptable", "Good", "Very Good"]
    assert 0 <= result["confidence"] <= 100
    assert set(result["probabilities"]) == {"Unacceptable", "Acceptable", "Good", "Very Good"}


@pytest.mark.anyio
async def test_invalid_category_is_rejected(client):
    invalid = {**SAMPLES[0], "safety": "extreme"}
    response = await client.post("/predict", json=invalid)
    assert response.status_code == 422
