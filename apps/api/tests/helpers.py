import uuid

from fastapi.testclient import TestClient

from app.main import app


def create_authenticated_client() -> TestClient:
    client = TestClient(app)
    unique_suffix = uuid.uuid4().hex[:8]
    response = client.post(
        "/auth/register",
        json={
            "email": f"test-{unique_suffix}@example.com",
            "name": "ResumeOS Test User",
            "password": "strong-password-123",
        },
    )
    assert response.status_code == 200, response.text
    return client
