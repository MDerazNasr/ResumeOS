import os
import unittest

from app.services.style_memory import (
    get_relevant_style_examples_for_user,
    refresh_draft_style_examples_for_user,
    store_accepted_style_example_for_user,
)
from tests.helpers import create_authenticated_client


class StyleMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "mock"
        self.client = create_authenticated_client()
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

    def test_retrieval_prefers_accepted_examples(self) -> None:
        accepted_text = "Delivered a backend feature with clearer ownership, measurable impact, and crisp technical framing."
        store_accepted_style_example_for_user(
            self.user["id"],
            self.resume_id,
            block_kind="bullet",
            block_label="Experience",
            text=accepted_text,
        )

        examples = get_relevant_style_examples_for_user(
            self.user["id"],
            self.resume_id,
            instruction="Make this stronger and more results-oriented",
            target_text="Built and shipped a production feature that improved a measurable product outcome.",
            preferred_kind="bullet",
            exclude_texts={"Built and shipped a production feature that improved a measurable product outcome."},
        )

        self.assertGreaterEqual(len(examples), 1)
        self.assertEqual(examples[0], accepted_text)

    def test_retrieval_prefers_varied_labels_before_duplicates(self) -> None:
        store_accepted_style_example_for_user(
            self.user["id"],
            self.resume_id,
            block_kind="bullet",
            block_label="Experience",
            text="Delivered backend improvements with clearer impact framing and tighter execution language.",
        )
        store_accepted_style_example_for_user(
            self.user["id"],
            self.resume_id,
            block_kind="bullet",
            block_label="Experience",
            text="Improved API reliability with measurable results and sharper technical ownership framing.",
        )
        store_accepted_style_example_for_user(
            self.user["id"],
            self.resume_id,
            block_kind="bullet",
            block_label="Projects",
            text="Built a product-facing system with explicit technical tradeoffs and stronger delivery framing.",
        )

        examples = get_relevant_style_examples_for_user(
            self.user["id"],
            self.resume_id,
            instruction="Make this stronger and more results-oriented",
            target_text="Built and shipped a production feature that improved a measurable product outcome.",
            preferred_kind="bullet",
            exclude_texts={"Built and shipped a production feature that improved a measurable product outcome."},
        )

        self.assertGreaterEqual(len(examples), 2)
        self.assertIn(
            "Built a product-facing system with explicit technical tradeoffs and stronger delivery framing.",
            examples[:2],
        )


if __name__ == "__main__":
    unittest.main()
