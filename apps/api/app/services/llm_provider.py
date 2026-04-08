import json
import os
from dataclasses import dataclass

import httpx


@dataclass
class EditSuggestionPrompt:
    block_kind: str
    block_label: str
    instruction: str
    text: str


class EditSuggestionProvider:
    def generate_rewrites(self, prompt: EditSuggestionPrompt) -> list[str]:
        raise NotImplementedError


class MockEditSuggestionProvider(EditSuggestionProvider):
    def generate_rewrites(self, prompt: EditSuggestionPrompt) -> list[str]:
        cleaned = prompt.text.rstrip(".")
        base_suffix = "clearer scope and stronger technical specificity"
        alternate_suffix = "more direct impact framing while preserving the original voice"

        if prompt.block_kind == "bullet":
            return [
                f"{cleaned}, with {base_suffix}.",
                f"{cleaned}, with {alternate_suffix}.",
            ]

        return [
            f"{cleaned} with {base_suffix}.",
            f"{cleaned} with {alternate_suffix}.",
        ]


class OpenAIEditSuggestionProvider(EditSuggestionProvider):
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate_rewrites(self, prompt: EditSuggestionPrompt) -> list[str]:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": 0.5,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You rewrite one resume block at a time. "
                            "Return strict JSON with a single key 'candidates' whose value is an array of 1-3 rewritten strings only."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Section: {prompt.block_label}\n"
                            f"Block kind: {prompt.block_kind}\n"
                            f"Instruction: {prompt.instruction}\n"
                            f"Original text: {prompt.text}"
                        ),
                    },
                ],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        payload = json.loads(content)
        candidates = payload.get("candidates", [])
        return [candidate.strip() for candidate in candidates if isinstance(candidate, str) and candidate.strip()]


def get_edit_suggestion_provider() -> EditSuggestionProvider:
    provider_name = os.getenv("RESUMEOS_LLM_PROVIDER", "mock").lower()

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("RESUMEOS_OPENAI_MODEL", "gpt-4o-mini")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when RESUMEOS_LLM_PROVIDER=openai.")

        return OpenAIEditSuggestionProvider(api_key=api_key, model=model, base_url=base_url)

    return MockEditSuggestionProvider()
