import os
import unittest

from tests.helpers import create_authenticated_client


class ResumeConstraintTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Constraint Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_constraints_round_trip(self) -> None:
        initial = self.client.get(f"/resumes/{self.resume_id}/constraints")
        self.assertEqual(initial.status_code, 200)
        self.assertEqual(initial.json()["rules"], [])

        updated = self.client.patch(
            f"/resumes/{self.resume_id}/constraints",
            json={"rules": ["Keep each bullet to one line.", "Avoid first-person voice."]},
        )
        self.assertEqual(updated.status_code, 200)
        payload = updated.json()
        self.assertEqual(
            payload["rules"],
            ["Keep each bullet to one line.", "Avoid first-person voice."],
        )

    def test_constraints_are_threaded_into_edit_generation(self) -> None:
        constraints_response = self.client.patch(
            f"/resumes/{self.resume_id}/constraints",
            json={"rules": ["Keep each bullet to one line."]},
        )
        self.assertEqual(constraints_response.status_code, 200)

        document_model = self.client.get(f"/resumes/{self.resume_id}/document-model").json()
        target_block_id = document_model["editableBlocks"][0]["id"]
        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/edit",
            json={"targetBlockId": target_block_id, "instruction": "Make this stronger."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["items"]), 0)
        self.assertEqual(payload["items"][0]["appliedConstraints"], ["Keep each bullet to one line."])
        self.assertNotIn("Keep each bullet to one line", payload["items"][0]["items"][0]["afterText"])


if __name__ == "__main__":
    unittest.main()
