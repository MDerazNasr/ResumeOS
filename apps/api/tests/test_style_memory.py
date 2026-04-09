import os
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.style_memory import get_relevant_style_examples_for_user, refresh_draft_style_examples_for_user


class StyleMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = TestClient(app)
        created = self.client.post("/resumes", json={"title": "Style Memory Test"})
        self.assertEqual(created.status_code, 200)
        self.resume_id = created.json()["id"]
        self.user = self.client.get("/me").json()

    def tearDown(self) -> None:
        os.environ.pop("RESUMEOS_LLM_PROVIDER", None)

    def test_refresh_persists_style_examples_from_current_draft(self) -> None:
        refresh_draft_style_examples_for_user(self.user["id"], self.resume_id)

        examples = get_relevant_style_examples_for_user(
            self.user["id"],
            self.resume_id,
            instruction="Make this more technical",
            target_text="Built and shipped a production feature that improved a measurable product outcome.",
            preferred_kind="bullet",
            exclude_texts={"Built and shipped a production feature that improved a measurable product outcome."},
        )

        self.assertGreaterEqual(len(examples), 1)
        self.assertTrue(all(isinstance(example, str) and example.strip() for example in examples))

    def test_retrieval_prefers_same_kind_examples_and_excludes_target_text(self) -> None:
        examples = get_relevant_style_examples_for_user(
            self.user["id"],
            self.resume_id,
            instruction="Make this stronger and more results-oriented",
            target_text="Built and shipped a production feature that improved a measurable product outcome.",
            preferred_kind="bullet",
            exclude_texts={"Built and shipped a production feature that improved a measurable product outcome."},
        )

        self.assertNotIn("Built and shipped a production feature that improved a measurable product outcome.", examples)
        self.assertTrue(any("Designed backend services" in example or "Building an AI-assisted resume IDE" in example for example in examples))


if __name__ == "__main__":
    unittest.main()
