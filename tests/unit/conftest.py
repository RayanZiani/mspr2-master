import pytest


@pytest.fixture
def sample_mesure():
    return {"temp": 29.0, "humidity": 55.0, "timestamp": "2025-01-01T00:00:00Z", "lot_id": "test-lot"}
