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


@dataclass
class ReviewSuggestionPrompt:
    instruction: str
    blocks: list[EditSuggestionPrompt]


@dataclass
class TailorSuggestionPrompt:
    instruction: str
    job_description: str
    blocks: list[EditSuggestionPrompt]


class EditSuggestionProvider:
    def generate_rewrites(self, prompt: EditSuggestionPrompt) -> list[str]:
        raise NotImplementedError

    def generate_review_rewrites(self, prompt: ReviewSuggestionPrompt) -> dict[str, list[str]]:
        raise NotImplementedError

    def generate_tailor_rewrites(self, prompt: TailorSuggestionPrompt) -> dict[str, list[str]]:
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

    def generate_review_rewrites(self, prompt: ReviewSuggestionPrompt) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}

        for block in prompt.blocks:
            result[block.text] = self.generate_rewrites(
                EditSuggestionPrompt(
                    block_kind=block.block_kind,
                    block_label=block.block_label,
                    instruction=prompt.instruction,
                    text=block.text,
                )
            )

        return result

    def generate_tailor_rewrites(self, prompt: TailorSuggestionPrompt) -> dict[str, list[str]]:
        emphasized_terms = _extract_emphasized_terms(prompt.job_description)
        emphasis = ", ".join(emphasized_terms[:3]) if emphasized_terms else "the target role"
        result: dict[str, list[str]] = {}

        for block in prompt.blocks:
            cleaned = block.text.rstrip(".")
            if block.block_kind == "bullet":
                candidates = [
                    f"{cleaned}, aligned more directly to {emphasis}.",
                    f"{cleaned}, with language that better matches {emphasis}.",
                ]
            else:
                candidates = [
                    f"{cleaned} with stronger alignment to {emphasis}.",
                    f"{cleaned} with wording that better matches {emphasis}.",
                ]
            result[block.text] = candidates

        return result


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

    def generate_review_rewrites(self, prompt: ReviewSuggestionPrompt) -> dict[str, list[str]]:
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
                            "You review a small set of resume blocks. "
                            "Return strict JSON with a single key 'items'. "
                            "Each item must include 'original' and 'candidates', where candidates is an array of 1-2 rewritten strings."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "instruction": prompt.instruction,
                                "blocks": [
                                    {
                                        "label": block.block_label,
                                        "kind": block.block_kind,
                                        "text": block.text,
                                    }
                                    for block in prompt.blocks
                                ],
                            }
                        ),
                    },
                ],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        payload = json.loads(content)
        items = payload.get("items", [])

        result: dict[str, list[str]] = {}
        for item in items:
            original = item.get("original")
            candidates = item.get("candidates", [])
            if isinstance(original, str):
                result[original] = [candidate.strip() for candidate in candidates if isinstance(candidate, str) and candidate.strip()]

        return result

    def generate_tailor_rewrites(self, prompt: TailorSuggestionPrompt) -> dict[str, list[str]]:
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
                            "You tailor a small set of resume blocks to a job description. "
                            "Return strict JSON with a single key 'items'. "
                            "Each item must include 'original' and 'candidates', where candidates is an array of 1-2 rewritten strings."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "instruction": prompt.instruction,
                                "job_description": prompt.job_description,
                                "blocks": [
                                    {
                                        "label": block.block_label,
                                        "kind": block.block_kind,
                                        "text": block.text,
                                    }
                                    for block in prompt.blocks
                                ],
                            }
                        ),
                    },
                ],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        payload = json.loads(content)
        items = payload.get("items", [])

        result: dict[str, list[str]] = {}
        for item in items:
            original = item.get("original")
            candidates = item.get("candidates", [])
            if isinstance(original, str):
                result[original] = [candidate.strip() for candidate in candidates if isinstance(candidate, str) and candidate.strip()]

        return result


def _extract_emphasized_terms(job_description: str) -> list[str]:
    preferred_terms = [
        "distributed systems",
        "machine learning",
        "backend",
        "python",
        "typescript",
        "api design",
        "leadership",
        "product thinking",
        "data",
        "infrastructure",
    ]
    lowered = job_description.lower()
    return [term for term in preferred_terms if term in lowered]


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
