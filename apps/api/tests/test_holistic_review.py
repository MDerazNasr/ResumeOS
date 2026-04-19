import unittest

from tests.helpers import create_authenticated_client


class HolisticReviewContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Holistic Review Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        draft_response = self.client.get(f"/resumes/{self.resume_id}/draft")
        self.assertEqual(draft_response.status_code, 200)
        self.draft = draft_response.json()

    def test_context_reports_resume_structure_without_compile(self) -> None:
        response = self.client.get(f"/resumes/{self.resume_id}/holistic-review/context")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["resumeId"], self.resume_id)
        self.assertIsNone(payload["latestCompileStatus"])
        self.assertIsNone(payload["pdfUrl"])
        self.assertGreater(payload["sourceLineCount"], 0)
        self.assertGreater(payload["editableBlockCount"], 0)

    def test_context_reports_latest_compile_artifact(self) -> None:
        compile_response = self.client.post(
            f"/resumes/{self.resume_id}/compile",
            json={"sourceTex": self.draft["sourceTex"], "draftVersion": self.draft["version"]},
        )
        self.assertEqual(compile_response.status_code, 200)

        response = self.client.get(f"/resumes/{self.resume_id}/holistic-review/context")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["latestCompileStatus"], "success")
        self.assertEqual(payload["latestCompileDraftVersion"], self.draft["version"])
        self.assertTrue(payload["pdfUrl"].endswith("/compile/latest.pdf"))
        self.assertGreaterEqual(payload["pdfSizeKb"], 1)
        self.assertGreaterEqual(len(payload["layoutSignals"]), 1)

    def test_context_reports_rule_driven_layout_signals(self) -> None:
        constraints_response = self.client.patch(
            f"/resumes/{self.resume_id}/constraints",
            json={"rules": ["Keep each bullet to one line."]},
        )
        self.assertEqual(constraints_response.status_code, 200)

        response = self.client.get(f"/resumes/{self.resume_id}/holistic-review/context")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("one-line-bullet-rule-active", payload["ruleSignals"])


if __name__ == "__main__":
    unittest.main()
