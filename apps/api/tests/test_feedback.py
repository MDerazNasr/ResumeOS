import unittest

from app.db.database import get_connection
from tests.helpers import create_authenticated_client


class FeedbackEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Feedback Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]

    def test_log_feedback_event(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/feedback",
            json={
                "suggestionMode": "review",
                "action": "dismiss",
                "suggestionSetId": "review-set-editable-bullet-1",
                "proposalId": "proposal-1",
                "targetBlockId": "editable-bullet-1",
            },
        )

        self.assertEqual(response.status_code, 204)

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT suggestion_mode, action, suggestion_set_id, proposal_id, target_block_id
                FROM feedback_events
                WHERE resume_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (self.resume_id,),
            ).fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["suggestion_mode"], "review")
        self.assertEqual(row["action"], "dismiss")
        self.assertEqual(row["suggestion_set_id"], "review-set-editable-bullet-1")
        self.assertEqual(row["proposal_id"], "proposal-1")
        self.assertEqual(row["target_block_id"], "editable-bullet-1")


if __name__ == "__main__":
    unittest.main()
