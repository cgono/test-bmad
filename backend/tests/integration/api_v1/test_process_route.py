from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_process_route_available() -> None:
    response = client.post("/v1/process")
    assert response.status_code == 200


def test_process_route_returns_envelope() -> None:
    response = client.post("/v1/process")
    data = response.json()

    assert data["status"] in {"success", "partial", "error"}
    assert isinstance(data["request_id"], str)
    assert data["request_id"]
    assert "data" in data
    assert "payload" not in data
