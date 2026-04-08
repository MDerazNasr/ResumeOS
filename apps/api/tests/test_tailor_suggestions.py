import os
import unittest

from fastapi.testclient import TestClient

from app.main import app


class TailorSuggestionsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Tailor Resume"}).json()
        self.resume_id = created["id"]

    def tearDown(self) -> None:
        os.environ.pop("RESUMEOS_LLM_PROVIDER", None)

    def test_generate_tailor_suggestions_returns_validated_sets(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/tailor",
            json={
                "jobDescription": (
                    "We are hiring a backend engineer with strong Python, distributed systems, API design, "
                    "and product thinking experience to improve developer-facing infrastructure."
                ),
                "instruction": "Tailor the resume toward the role.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload["items"]), 1)

        for suggestion_set in payload["items"]:
            self.assertIn("Tailor suggestions for", suggestion_set["title"])
            self.assertGreaterEqual(len(suggestion_set["items"]), 1)

            for proposal in suggestion_set["items"]:
                self.assertEqual(proposal["status"], "validated")
                self.assertTrue(proposal["validation"]["isValid"])


if __name__ == "__main__":
    unittest.main()
