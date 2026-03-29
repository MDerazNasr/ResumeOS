import unittest

from fastapi.testclient import TestClient

from app.main import app


class CompileFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Compile Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        draft_response = self.client.get(f"/resumes/{self.resume_id}/draft")
        self.assertEqual(draft_response.status_code, 200)
        self.draft = draft_response.json()

    def test_compile_success_returns_pdf_url(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/compile",
            json={"sourceTex": self.draft["sourceTex"], "draftVersion": self.draft["version"]},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertTrue(payload["pdfUrl"].endswith("/compile/latest.pdf"))

    def test_compile_failure_returns_error_logs(self) -> None:
        broken_source = self.draft["sourceTex"].replace("\\end{document}", "")

        response = self.client.post(
            f"/resumes/{self.resume_id}/compile",
            json={"sourceTex": broken_source, "draftVersion": self.draft["version"]},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "error")
        self.assertGreaterEqual(len(payload["logs"]), 1)

    def test_compile_conflict_returns_409(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/compile",
            json={"sourceTex": self.draft["sourceTex"], "draftVersion": 999},
        )

        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
