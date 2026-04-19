import os
import unittest

from tests.helpers import create_authenticated_client


class HolisticReviewSuggestionTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Holistic Review Suggestion Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_generate_holistic_review_suggestions(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/holistic-review",
            json={"instruction": "Review this resume for flow, density, and wording weaknesses."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["items"]), 0)
        self.assertTrue(all(item["mode"] == "review" for item in payload["items"]))
        self.assertTrue(all(item["title"].startswith("Holistic Review suggestions") for item in payload["items"]))
        self.assertTrue(all(proposal["validation"]["isValid"] for item in payload["items"] for proposal in item["items"]))


if __name__ == "__main__":
    unittest.main()
