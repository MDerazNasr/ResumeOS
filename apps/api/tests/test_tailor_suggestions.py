import os
import unittest

from tests.helpers import create_authenticated_client


class TailorSuggestionsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
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
            self.assertEqual(suggestion_set["mode"], "tailor")
            self.assertTrue(
                suggestion_set["title"] in {
                    "Backend / API alignment",
                    "Systems / infrastructure alignment",
                    "Ownership / collaboration alignment",
                    "General role alignment",
                }
            )
            self.assertGreaterEqual(len(suggestion_set["items"]), 1)
            self.assertGreaterEqual(len(suggestion_set["styleExamples"]), 1)

            for proposal in suggestion_set["items"]:
                self.assertEqual(proposal["status"], "validated")
                self.assertTrue(proposal["validation"]["isValid"])

    def test_generate_tailor_suggestions_groups_by_job_description_themes(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/tailor",
            json={
                "jobDescription": (
                    "Senior backend engineer working on APIs, distributed systems, platform infrastructure, "
                    "and cross-functional product ownership."
                ),
                "instruction": "Tailor the resume toward the role.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        titles = {item["title"] for item in payload["items"]}

        self.assertIn("Backend / API alignment", titles)
        self.assertIn("Systems / infrastructure alignment", titles)
        self.assertIn("Ownership / collaboration alignment", titles)

    def test_generate_tailor_suggestions_creates_pre_tailor_snapshot(self) -> None:
        before = self.client.get(f"/resumes/{self.resume_id}/snapshots").json()
        self.assertEqual(len(before["items"]), 0)

        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/tailor",
            json={
                "jobDescription": "Senior Backend Engineer focused on Python, API design, and distributed systems.",
                "instruction": "Tailor the resume toward the role.",
            },
        )

        self.assertEqual(response.status_code, 200)

        after = self.client.get(f"/resumes/{self.resume_id}/snapshots").json()
        self.assertEqual(len(after["items"]), 1)
        self.assertIn("Before tailoring:", after["items"][0]["name"])


if __name__ == "__main__":
    unittest.main()
