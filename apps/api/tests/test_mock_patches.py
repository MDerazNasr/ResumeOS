import unittest

from fastapi.testclient import TestClient

from app.main import app


class MockPatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Mock Patch Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_mock_patch_proposals_are_prevalidated(self) -> None:
        response = self.client.get(f"/resumes/{self.resume_id}/patches/mock")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["items"]), 0)
        self.assertTrue(all(item["validation"]["isValid"] for item in payload["items"]))

    def test_mock_patch_proposals_target_editable_blocks(self) -> None:
        document_model = self.client.get(f"/resumes/{self.resume_id}/document-model").json()
        editable_ids = {block["id"] for block in document_model["editableBlocks"]}

        response = self.client.get(f"/resumes/{self.resume_id}/patches/mock")
        self.assertEqual(response.status_code, 200)

        for item in response.json()["items"]:
            self.assertIn(item["targetBlockId"], editable_ids)


if __name__ == "__main__":
    unittest.main()
