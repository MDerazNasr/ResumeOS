import unittest

from tests.helpers import create_authenticated_client


class PatchValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Patch Validation Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        document_model = self.client.get(f"/resumes/{self.resume_id}/document-model").json()
        self.target_block = next(block for block in document_model["editableBlocks"] if block["kind"] == "bullet")

    def test_exact_editable_block_target_is_valid(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/patches/validate",
            json={
                "targetBlockId": self.target_block["id"],
                "startLine": self.target_block["startLine"],
                "endLine": self.target_block["endLine"],
                "beforeText": self.target_block["text"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["isValid"])

    def test_mismatched_before_text_is_rejected(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/patches/validate",
            json={
                "targetBlockId": self.target_block["id"],
                "startLine": self.target_block["startLine"],
                "endLine": self.target_block["endLine"],
                "beforeText": "stale text that no longer matches",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["isValid"])

    def test_unknown_target_block_is_rejected(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/patches/validate",
            json={
                "targetBlockId": "editable-bullet-9999",
                "startLine": self.target_block["startLine"],
                "endLine": self.target_block["endLine"],
                "beforeText": self.target_block["text"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["isValid"])


if __name__ == "__main__":
    unittest.main()
