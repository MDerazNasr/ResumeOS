import os
import unittest

from tests.helpers import create_authenticated_client


class EditSuggestionTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Edit Suggestion Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        document_model = self.client.get(f"/resumes/{self.resume_id}/document-model").json()
        self.target_block = next(block for block in document_model["editableBlocks"] if block["kind"] == "bullet")

    def test_generate_edit_suggestions_for_block(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/edit",
            json={
                "targetBlockId": self.target_block["id"],
                "instruction": "Make this stronger and more results-oriented",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["mode"], "edit")
        self.assertGreaterEqual(len(payload["items"][0]["styleExamples"]), 1)
        self.assertEqual(payload["items"][0]["appliedConstraints"], [])
        self.assertNotIn(self.target_block["text"], payload["items"][0]["styleExamples"])
        self.assertGreater(len(payload["items"][0]["items"]), 0)
        self.assertTrue(all(item["validation"]["isValid"] for item in payload["items"][0]["items"]))

    def test_generate_edit_suggestions_rejects_unknown_block(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/edit",
            json={
                "targetBlockId": "editable-bullet-missing",
                "instruction": "Make this stronger",
            },
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
