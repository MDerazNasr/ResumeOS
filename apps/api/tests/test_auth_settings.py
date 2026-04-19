import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class AuthSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.unique_suffix = uuid.uuid4().hex[:8]

    def test_google_status_reflects_configuration(self) -> None:
        response = self.client.get("/auth/google/status")
        self.assertEqual(response.status_code, 200)
        self.assertIn("configured", response.json())

    def test_google_start_redirects_when_configured(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "RESUMEOS_GOOGLE_CLIENT_ID": "test-client-id",
                "RESUMEOS_GOOGLE_CLIENT_SECRET": "test-client-secret",
                "RESUMEOS_GOOGLE_REDIRECT_URI": "http://127.0.0.1:8000/auth/google/callback",
            },
            clear=False,
        ):
            response = self.client.get("/auth/google/start", follow_redirects=False)

        self.assertEqual(response.status_code, 307)
        self.assertIn("accounts.google.com", response.headers["location"])
        self.assertIn("resumeos_google_state", response.cookies)

    def test_google_callback_creates_session_and_settings_round_trip(self) -> None:
        email = f"settings-test-{self.unique_suffix}@example.com"
        client = TestClient(app)

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
                "sub": f"google-sub-{self.unique_suffix}",
                "email": email,
                "name": "Settings Test",
            },
        ):
            start = client.get("/auth/google/start", follow_redirects=False)
            state = start.cookies.get("resumeos_google_state")
            callback = client.get(f"/auth/google/callback?code=test-code&state={state}", follow_redirects=False)

        self.assertEqual(callback.status_code, 307)
        self.assertIn("resumeos_session", callback.cookies)

        settings_before = client.get("/settings")
        self.assertEqual(settings_before.status_code, 200)
        self.assertEqual(settings_before.json()["editorMode"], "standard")
        self.assertEqual(settings_before.json()["themeMode"], "light")

        settings_after = client.patch("/settings", json={"editorMode": "vim", "themeMode": "light"})
        self.assertEqual(settings_after.status_code, 200)
        self.assertEqual(settings_after.json()["editorMode"], "vim")
        self.assertEqual(settings_after.json()["themeMode"], "light")

        me = client.get("/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], email)

    def test_google_callback_requires_matching_state(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "RESUMEOS_GOOGLE_CLIENT_ID": "test-client-id",
                "RESUMEOS_GOOGLE_CLIENT_SECRET": "test-client-secret",
                "RESUMEOS_GOOGLE_REDIRECT_URI": "http://127.0.0.1:8000/auth/google/callback",
            },
            clear=False,
        ):
            response = self.client.get("/auth/google/callback?code=test-code&state=wrong-state", follow_redirects=False)

        self.assertEqual(response.status_code, 400)

    def test_google_callback_accepts_valid_signed_state_without_cookie(self) -> None:
        client = TestClient(app)
        email = f"signed-state-{self.unique_suffix}@example.com"

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
                "sub": f"google-sub-signed-{self.unique_suffix}",
                "email": email,
                "name": "Signed State Test",
            },
        ):
            start = client.get("/auth/google/start", follow_redirects=False)
            state = start.cookies.get("resumeos_google_state")
            client.cookies.clear()
            callback = client.get(f"/auth/google/callback?code=test-code&state={state}", follow_redirects=False)

        self.assertEqual(callback.status_code, 307)
        self.assertIn("resumeos_session", callback.cookies)

    def test_me_requires_authenticated_session(self) -> None:
        response = self.client.get("/me")
        self.assertEqual(response.status_code, 401)

    def test_settings_require_authenticated_session(self) -> None:
        response = self.client.get("/settings")
        self.assertEqual(response.status_code, 401)

    def test_resume_routes_require_authenticated_session(self) -> None:
        response = self.client.get("/resumes")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
