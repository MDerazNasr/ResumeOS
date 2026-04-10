import unittest

from tests.helpers import create_authenticated_client


class SnapshotFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Snapshot Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_create_snapshot_from_current_draft(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/snapshots",
            json={"name": "Before edits"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["name"], "Before edits")
        self.assertEqual(payload["resumeId"], self.resume_id)

    def test_list_snapshots_returns_created_snapshot(self) -> None:
        self.client.post(f"/resumes/{self.resume_id}/snapshots", json={"name": "Before edits"})

        response = self.client.get(f"/resumes/{self.resume_id}/snapshots")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_get_snapshot_returns_snapshot_source(self) -> None:
        draft = self.client.get(f"/resumes/{self.resume_id}/draft").json()
        updated_source = draft["sourceTex"] + "\n% snapshot compare marker\n"
        self.client.put(
            f"/resumes/{self.resume_id}/draft",
            json={"sourceTex": updated_source, "version": draft["version"]},
        )

        snapshot = self.client.post(
            f"/resumes/{self.resume_id}/snapshots",
            json={"name": "Compare target"},
        ).json()

        response = self.client.get(f"/resumes/{self.resume_id}/snapshots/{snapshot['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], snapshot["id"])
        self.assertIn("% snapshot compare marker", response.json()["sourceTex"])

    def test_restore_snapshot_updates_working_draft(self) -> None:
        draft = self.client.get(f"/resumes/{self.resume_id}/draft").json()

        self.client.put(
            f"/resumes/{self.resume_id}/draft",
            json={"sourceTex": draft["sourceTex"] + "\n% edited after snapshot\n", "version": draft["version"]},
        )

        snapshot = self.client.post(
            f"/resumes/{self.resume_id}/snapshots",
            json={"name": "Edited version"},
        ).json()

        latest_draft = self.client.get(f"/resumes/{self.resume_id}/draft").json()
        self.client.put(
            f"/resumes/{self.resume_id}/draft",
            json={"sourceTex": latest_draft["sourceTex"] + "\n% later draft change\n", "version": latest_draft["version"]},
        )

        restored = self.client.post(
            f"/resumes/{self.resume_id}/snapshots/restore",
            json={"snapshotId": snapshot["id"]},
        )

        self.assertEqual(restored.status_code, 200)
        self.assertIn("% edited after snapshot", restored.json()["sourceTex"])
        self.assertNotIn("% later draft change", restored.json()["sourceTex"])


if __name__ == "__main__":
    unittest.main()
