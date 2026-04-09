import unittest

from fastapi.testclient import TestClient

from app.main import app


class PatchApplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Patch Apply Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        self.proposal = self.client.get(f"/resumes/{self.resume_id}/patch-sets/seeded").json()["items"][0]["items"][0]

    def test_valid_seeded_patch_can_be_applied(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/patches/apply",
            json={
                "targetBlockId": self.proposal["targetBlockId"],
                "startLine": self.proposal["startLine"],
                "endLine": self.proposal["endLine"],
                "beforeText": self.proposal["beforeText"],
                "afterText": self.proposal["afterText"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.proposal["afterText"], response.json()["sourceTex"])
        self.assertGreater(response.json()["version"], 1)

    def test_stale_patch_is_rejected(self) -> None:
        first_apply = self.client.post(
            f"/resumes/{self.resume_id}/patches/apply",
            json={
                "targetBlockId": self.proposal["targetBlockId"],
                "startLine": self.proposal["startLine"],
                "endLine": self.proposal["endLine"],
                "beforeText": self.proposal["beforeText"],
                "afterText": self.proposal["afterText"],
            },
        )
        self.assertEqual(first_apply.status_code, 200)

        stale_response = self.client.post(
            f"/resumes/{self.resume_id}/patches/apply",
            json={
                "targetBlockId": self.proposal["targetBlockId"],
                "startLine": self.proposal["startLine"],
                "endLine": self.proposal["endLine"],
                "beforeText": self.proposal["beforeText"],
                "afterText": self.proposal["afterText"],
            },
        )

        self.assertEqual(stale_response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
