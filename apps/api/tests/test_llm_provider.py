import os
import unittest

from app.services.llm_provider import OpenAIEditSuggestionProvider, get_edit_suggestion_provider


class LlmProviderTests(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("RESUMEOS_LLM_PROVIDER", None)
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("RESUMEOS_GEMINI_MODEL", None)
        os.environ.pop("GEMINI_BASE_URL", None)

    def test_gemini_provider_uses_openai_compatible_transport(self) -> None:
        os.environ["RESUMEOS_LLM_PROVIDER"] = "gemini"
        os.environ["GEMINI_API_KEY"] = "test-key"
        os.environ["RESUMEOS_GEMINI_MODEL"] = "gemini-test-model"

        provider = get_edit_suggestion_provider()

        self.assertIsInstance(provider, OpenAIEditSuggestionProvider)
        self.assertEqual(provider.api_key, "test-key")
        self.assertEqual(provider.model, "gemini-test-model")
        self.assertEqual(provider.base_url, "https://generativelanguage.googleapis.com/v1beta/openai")


if __name__ == "__main__":
    unittest.main()
