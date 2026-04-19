import os
import unittest

from tests.helpers import create_authenticated_client


class LayoutHeuristicsTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Layout Heuristic Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        constraints_response = self.client.patch(
            f"/resumes/{self.resume_id}/constraints",
            json={"rules": ["Keep each bullet to one line."]},
        )
        self.assertEqual(constraints_response.status_code, 200)

    def test_holistic_review_prioritizes_bullets_when_one_line_rule_is_active(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/holistic-review",
            json={"instruction": "Review this resume for flow and density."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["items"]), 0)
        first_set = payload["items"][0]
        self.assertGreater(len(first_set["items"]), 0)
        self.assertIn("Keep each bullet to one line.", first_set["appliedConstraints"])


if __name__ == "__main__":
    unittest.main()
