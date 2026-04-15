import unittest
import json
from unittest.mock import patch

from tests.helpers import create_authenticated_client


class ChatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = create_authenticated_client()
        created = self.client.post("/resumes", json={"title": "Chat Test Resume"}).json()
        self.resume_id = created["id"]

    def test_chat_thread_is_created_for_resume(self) -> None:
        response = self.client.get(f"/resumes/{self.resume_id}/chat")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["resumeId"], self.resume_id)
        self.assertEqual(payload["messages"], [])

    def test_chat_message_persists_user_and_assistant_messages(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={"content": "Review my resume and suggest stronger wording."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["thread"]["messages"]), 2)
        self.assertEqual(payload["thread"]["messages"][0]["role"], "user")
        self.assertEqual(payload["thread"]["messages"][1]["role"], "assistant")
        self.assertEqual(payload["assistantMessageId"], payload["thread"]["messages"][1]["id"])
        self.assertEqual(payload["chatIntent"], "review")
        self.assertEqual(payload["intentSource"], "message")
        self.assertIsNotNone(payload["generatedPatchSetSummary"])
        self.assertGreaterEqual(len(payload["patchSets"]), 1)

    def test_chat_tailor_message_can_return_patch_sets(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={
                "content": "Tailor this resume for a backend platform role focused on distributed systems, APIs, infrastructure reliability, and cross-functional ownership."
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["chatIntent"], "tailor")
        self.assertEqual(payload["intentSource"], "message")
        self.assertGreaterEqual(len(payload["patchSets"]), 1)

    def test_question_only_chat_returns_context_without_patch_sets(self) -> None:
        response = self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={"content": "What do you notice about the current structure of this resume?"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["chatIntent"], "question")
        self.assertEqual(payload["intentSource"], "message")
        self.assertEqual(payload["patchSets"], [])

    def test_chat_reply_receives_recent_message_history(self) -> None:
        self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={"content": "What do you notice about the structure of this resume?"},
        )

        captured_prompt = {}

        class StubProvider:
            def generate_chat_reply(self, prompt):
                captured_prompt["recent_messages"] = prompt.recent_messages
                return "Stubbed follow-up reply."

        with patch("app.services.chat.get_edit_suggestion_provider", return_value=StubProvider()):
            response = self.client.post(
                f"/resumes/{self.resume_id}/chat/messages",
                json={"content": "And what would you improve next?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(captured_prompt["recent_messages"]), 2)
        self.assertEqual(captured_prompt["recent_messages"][-1][0], "assistant")

    def test_follow_up_message_inherits_last_review_intent(self) -> None:
        self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={"content": "Review my resume and suggest stronger wording."},
        )

        response = self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={"content": "Make them shorter and more direct."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["chatIntent"], "review")
        self.assertEqual(payload["intentSource"], "history")
        self.assertGreaterEqual(len(payload["patchSets"]), 1)

    def test_follow_up_message_can_continue_last_tailor_request(self) -> None:
        self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={
                "content": "Tailor this resume for a backend platform role focused on distributed systems, APIs, infrastructure reliability, and cross-functional ownership."
            },
        )

        response = self.client.post(
            f"/resumes/{self.resume_id}/chat/messages",
            json={"content": "Also make it emphasize leadership and ownership more."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["chatIntent"], "tailor")
        self.assertEqual(payload["intentSource"], "history")
        self.assertGreaterEqual(len(payload["patchSets"]), 1)

    def test_chat_stream_endpoint_returns_start_delta_and_complete_events(self) -> None:
        with self.client.stream(
            "POST",
            f"/resumes/{self.resume_id}/chat/messages/stream",
            json={"content": "Review my resume and suggest stronger wording."},
        ) as response:
            self.assertEqual(response.status_code, 200)
            lines = [line for line in response.iter_lines() if line]

        events = [json.loads(line) for line in lines]
        self.assertEqual(events[0]["type"], "start")
        self.assertEqual(events[0]["chatIntent"], "review")
        self.assertTrue(any(event["type"] == "delta" for event in events))
        self.assertEqual(events[-1]["type"], "complete")
        self.assertEqual(events[-1]["response"]["chatIntent"], "review")


if __name__ == "__main__":
    unittest.main()
