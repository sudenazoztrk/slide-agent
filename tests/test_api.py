from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_without_api_key_header():
    response = client.post("/ask", json={"question": "test sorusu"})

    assert response.status_code == 422


def test_ask_with_wrong_api_key():
    response = client.post(
        "/ask",
        json={"question": "test sorusu"},
        headers={"X-API-Key": "yanlis-bir-key"}
    )

    assert response.status_code == 401