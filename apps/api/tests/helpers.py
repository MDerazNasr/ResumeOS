import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def create_authenticated_client() -> TestClient:
    client = TestClient(app)
    unique_suffix = uuid.uuid4().hex[:8]
    with patch.dict(
        "os.environ",
        {
            "RESUMEOS_GOOGLE_CLIENT_ID": "test-client-id",
            "RESUMEOS_GOOGLE_CLIENT_SECRET": "test-client-secret",
            "RESUMEOS_GOOGLE_REDIRECT_URI": "http://127.0.0.1:8000/auth/google/callback",
        },
        clear=False,
    ), patch("app.services.auth.exchange_google_code", return_value={"access_token": "test-access-token"}), patch(
        "app.services.auth.fetch_google_profile",
        return_value={
            "sub": f"google-sub-{unique_suffix}",
            "email": f"test-{unique_suffix}@example.com",
            "name": "ResumeOS Test User",
        },
    ):
        start = client.get("/auth/google/start", follow_redirects=False)
        assert start.status_code == 307, start.text
        state = start.cookies.get("resumeos_google_state")
        response = client.get(f"/auth/google/callback?code=test-code&state={state}", follow_redirects=False)
    assert response.status_code == 307, response.text
    return client
