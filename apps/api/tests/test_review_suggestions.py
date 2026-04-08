import os
import unittest

from fastapi.testclient import TestClient

from app.main import app


class ReviewSuggestionTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Review Suggestion Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_generate_review_suggestions(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/review",
            json={"instruction": "Find the weakest blocks and make them sharper"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["items"]), 0)
        self.assertTrue(all(item["items"] for item in payload["items"]))
        self.assertTrue(all(proposal["validation"]["isValid"] for item in payload["items"] for proposal in item["items"]))


if __name__ == "__main__":
    unittest.main()
