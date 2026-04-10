import unittest

from fastapi.testclient import TestClient

from app.main import app


class AuthSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_register_creates_session_and_returns_user(self) -> None:
        response = self.client.post(
            "/auth/register",
            json={
                "email": "auth-test@example.com",
                "name": "Auth Test",
                "password": "strong-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "auth-test@example.com")
        self.assertIn("resumeos_session", response.cookies)

    def test_login_and_settings_round_trip(self) -> None:
        self.client.post(
            "/auth/register",
            json={
                "email": "settings-test@example.com",
                "name": "Settings Test",
                "password": "strong-password-123",
            },
        )
        client = TestClient(app)
        login = client.post(
            "/auth/login",
            json={
                "email": "settings-test@example.com",
                "password": "strong-password-123",
            },
        )

        self.assertEqual(login.status_code, 200)
        self.assertIn("resumeos_session", login.cookies)

        settings_before = client.get("/settings")
        self.assertEqual(settings_before.status_code, 200)
        self.assertEqual(settings_before.json()["editorMode"], "standard")

        settings_after = client.patch("/settings", json={"editorMode": "vim"})
        self.assertEqual(settings_after.status_code, 200)
        self.assertEqual(settings_after.json()["editorMode"], "vim")

        me = client.get("/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "settings-test@example.com")

    def test_me_falls_back_to_dev_user_without_session(self) -> None:
        response = self.client.get("/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "dev@resumeos.local")


if __name__ == "__main__":
    unittest.main()
