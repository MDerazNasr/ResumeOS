import os
import unittest

from tests.helpers import create_authenticated_client


class ConstraintEnforcementTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Constraint Enforcement Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_one_line_bullet_rule_keeps_generated_bullets_short(self) -> None:
        updated = self.client.patch(
            f"/resumes/{self.resume_id}/constraints",
            json={"rules": ["Keep each bullet to one line."]},
        )
        self.assertEqual(updated.status_code, 200)

        document_model = self.client.get(f"/resumes/{self.resume_id}/document-model").json()
        target_block = next(block for block in document_model["editableBlocks"] if block["kind"] == "bullet")

        response = self.client.post(
            f"/resumes/{self.resume_id}/suggestions/edit",
            json={"targetBlockId": target_block["id"], "instruction": "Make this stronger."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(len(payload["items"][0]["items"]), 0)
        for proposal in payload["items"][0]["items"]:
            self.assertLessEqual(len(" ".join(proposal["afterText"].split())), 95)


if __name__ == "__main__":
    unittest.main()
