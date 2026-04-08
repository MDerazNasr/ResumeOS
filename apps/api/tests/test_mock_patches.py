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
        self.assertTrue(all(item["items"] for item in payload["items"]))
        self.assertTrue(all(item["mode"] == "mock" for item in payload["items"]))
        self.assertTrue(
            all(proposal["validation"]["isValid"] for item in payload["items"] for proposal in item["items"])
        )

    def test_mock_patch_proposals_target_editable_blocks(self) -> None:
        document_model = self.client.get(f"/resumes/{self.resume_id}/document-model").json()
        editable_ids = {block["id"] for block in document_model["editableBlocks"]}

        response = self.client.get(f"/resumes/{self.resume_id}/patches/mock")
        self.assertEqual(response.status_code, 200)

        for item in response.json()["items"]:
            for proposal in item["items"]:
                self.assertIn(proposal["targetBlockId"], editable_ids)

    def test_mock_patch_sets_can_be_retried_with_a_new_seed(self) -> None:
        initial = self.client.get(f"/resumes/{self.resume_id}/patches/mock").json()
        retried = self.client.get(f"/resumes/{self.resume_id}/patches/mock?seed=1").json()

        self.assertEqual(initial["items"][0]["id"], retried["items"][0]["id"])
        self.assertNotEqual(
            initial["items"][0]["items"][0]["afterText"],
            retried["items"][0]["items"][0]["afterText"],
        )


if __name__ == "__main__":
    unittest.main()
