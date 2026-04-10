import unittest
import uuid

from fastapi.testclient import TestClient

from app.main import app


class AuthSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.unique_suffix = uuid.uuid4().hex[:8]

    def test_register_creates_session_and_returns_user(self) -> None:
        response = self.client.post(
            "/auth/register",
            json={
                "email": f"auth-test-{self.unique_suffix}@example.com",
                "name": "Auth Test",
                "password": "strong-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], f"auth-test-{self.unique_suffix}@example.com")
        self.assertIn("resumeos_session", response.cookies)

    def test_login_and_settings_round_trip(self) -> None:
        email = f"settings-test-{self.unique_suffix}@example.com"
        self.client.post(
            "/auth/register",
            json={
                "email": email,
                "name": "Settings Test",
                "password": "strong-password-123",
            },
        )
        client = TestClient(app)
        login = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "strong-password-123",
            },
        )

        self.assertEqual(login.status_code, 200)
        self.assertIn("resumeos_session", login.cookies)

        settings_before = client.get("/settings")
        self.assertEqual(settings_before.status_code, 200)
        self.assertEqual(settings_before.json()["editorMode"], "standard")
        self.assertEqual(settings_before.json()["themeMode"], "dark")

        settings_after = client.patch("/settings", json={"editorMode": "vim", "themeMode": "light"})
        self.assertEqual(settings_after.status_code, 200)
        self.assertEqual(settings_after.json()["editorMode"], "vim")
        self.assertEqual(settings_after.json()["themeMode"], "light")

        me = client.get("/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], email)

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
