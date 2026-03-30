import unittest

from fastapi.testclient import TestClient

from app.main import app


class DocumentModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Document Model Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_document_model_marks_preamble_and_scaffold_as_protected(self) -> None:
        response = self.client.get(f"/resumes/{self.resume_id}/document-model")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        protected_kinds = {region["kind"] for region in payload["protectedRegions"]}

        self.assertIn("preamble", protected_kinds)
        self.assertIn("scaffold", protected_kinds)

    def test_document_model_extracts_summary_and_bullets_as_editable_blocks(self) -> None:
        response = self.client.get(f"/resumes/{self.resume_id}/document-model")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        editable_blocks = payload["editableBlocks"]

        self.assertTrue(any(block["kind"] == "paragraph" and block["label"] == "Summary" for block in editable_blocks))
        self.assertTrue(any(block["kind"] == "bullet" and block["label"] == "Experience" for block in editable_blocks))


if __name__ == "__main__":
    unittest.main()
