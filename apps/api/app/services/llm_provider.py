import json
import os
from collections.abc import Iterator
from dataclasses import dataclass

import httpx


@dataclass
class EditSuggestionPrompt:
    block_kind: str
    block_label: str
    instruction: str
    text: str
    style_examples: list[str]


@dataclass
class ReviewSuggestionPrompt:
    instruction: str
    blocks: list[EditSuggestionPrompt]


@dataclass
class TailorSuggestionPrompt:
    instruction: str
    job_description: str
    blocks: list[EditSuggestionPrompt]


@dataclass
class ChatConversationPrompt:
    user_message: str
    detected_intent: str
    intent_source: str
    recent_messages: list[tuple[str, str]]
    editable_block_count: int
    style_examples: list[str]
    patch_set_summary: str | None
    recent_feedback_summary: str | None


class EditSuggestionProvider:
    def generate_rewrites(self, prompt: EditSuggestionPrompt) -> list[str]:
        raise NotImplementedError

    def generate_review_rewrites(self, prompt: ReviewSuggestionPrompt) -> dict[str, list[str]]:
        raise NotImplementedError

    def generate_tailor_rewrites(self, prompt: TailorSuggestionPrompt) -> dict[str, list[str]]:
        raise NotImplementedError

    def generate_chat_reply(self, prompt: ChatConversationPrompt) -> str:
        raise NotImplementedError

    def stream_chat_reply(self, prompt: ChatConversationPrompt) -> Iterator[str]:
        for chunk in _chunk_text(self.generate_chat_reply(prompt)):
            yield chunk


class MockEditSuggestionProvider(EditSuggestionProvider):
    def generate_rewrites(self, prompt: EditSuggestionPrompt) -> list[str]:
        cleaned = prompt.text.rstrip(".")
        style_tone = _style_tone_suffix(prompt.style_examples)
        base_suffix = f"clearer scope, stronger technical specificity, and {style_tone}"
        alternate_suffix = f"more direct impact framing while preserving the user's {style_tone}"

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
                    style_examples=block.style_examples,
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

    def generate_chat_reply(self, prompt: ChatConversationPrompt) -> str:
        style_hint = prompt.style_examples[0] if prompt.style_examples else "No strong prior style example was available."
        history_hint = (
            f" I also considered {len(prompt.recent_messages)} recent chat message"
            f"{'' if len(prompt.recent_messages) == 1 else 's'}."
            if prompt.recent_messages
            else ""
        )
        follow_up_hint = " I treated this as a follow-up to the recent conversation." if prompt.intent_source == "history" else ""
        feedback_hint = f" Recent patch decisions: {prompt.recent_feedback_summary}." if prompt.recent_feedback_summary else ""
        if prompt.detected_intent == "question":
            return (
                f"I read that as a resume question. The current draft has {prompt.editable_block_count} editable blocks. "
                f"Closest style memory example: \"{style_hint}\".{history_hint}{follow_up_hint}{feedback_hint} "
                "Ask for a review, an edit, or a tailored pass when you want concrete patch sets."
            )

        if prompt.detected_intent == "review":
            return (
                f"I generated a review pass over the current draft. {prompt.patch_set_summary or 'No valid review patch sets were generated.'}"
                f"{history_hint}{follow_up_hint}{feedback_hint} Review the suggested wording changes inline before applying them."
            )

        if prompt.detected_intent == "tailor":
            return (
                f"I treated this as a tailoring request against the target role. {prompt.patch_set_summary or 'No valid tailoring patch sets were generated.'}"
                f"{history_hint}{follow_up_hint}{feedback_hint} Review the tailored changes inline and keep only the ones that match the role."
            )

        return (
            f"I generated targeted edit suggestions for the current draft. {prompt.patch_set_summary or 'No valid edit patch sets were generated.'}"
            f"{history_hint}{follow_up_hint}{feedback_hint} Review the edits inline before applying them."
        )


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
                            f"Style examples: {json.dumps(prompt.style_examples)}\n"
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
                                        "style_examples": block.style_examples,
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
                                        "style_examples": block.style_examples,
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

    def generate_chat_reply(self, prompt: ChatConversationPrompt) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": 0.4,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are the chat layer for an AI-assisted resume editor. "
                            "Respond concisely and format the reply to match the request type. "
                            "For question intent, answer the question using the provided resume context. "
                            "For review/edit/tailor intents, briefly explain what the generated patch sets cover and remind the user to review them inline. "
                            "When intent_source is history, acknowledge that the message was treated as a follow-up."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "user_message": prompt.user_message,
                                "detected_intent": prompt.detected_intent,
                                "intent_source": prompt.intent_source,
                                "recent_messages": prompt.recent_messages,
                                "editable_block_count": prompt.editable_block_count,
                                "style_examples": prompt.style_examples,
                                "patch_set_summary": prompt.patch_set_summary,
                                "recent_feedback_summary": prompt.recent_feedback_summary,
                            }
                        ),
                    },
                ],
            },
            timeout=20.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return content.strip()

    def stream_chat_reply(self, prompt: ChatConversationPrompt) -> Iterator[str]:
        with httpx.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": 0.4,
                "stream": True,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are the chat layer for an AI-assisted resume editor. "
                            "Respond concisely and format the reply to match the request type. "
                            "For question intent, answer the question using the provided resume context. "
                            "For review/edit/tailor intents, briefly explain what the generated patch sets cover and remind the user to review them inline. "
                            "When intent_source is history, acknowledge that the message was treated as a follow-up."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "user_message": prompt.user_message,
                                "detected_intent": prompt.detected_intent,
                                "intent_source": prompt.intent_source,
                                "recent_messages": prompt.recent_messages,
                                "editable_block_count": prompt.editable_block_count,
                                "style_examples": prompt.style_examples,
                                "patch_set_summary": prompt.patch_set_summary,
                                "recent_feedback_summary": prompt.recent_feedback_summary,
                            }
                        ),
                    },
                ],
            },
            timeout=20.0,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                    delta = data["choices"][0]["delta"].get("content")
                except (KeyError, IndexError, json.JSONDecodeError):
                    continue
                if isinstance(delta, str) and delta:
                    yield delta


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


def _style_tone_suffix(style_examples: list[str]) -> str:
    if not style_examples:
        return "a crisp resume cadence"

    average_word_count = sum(len(example.split()) for example in style_examples) / len(style_examples)
    if average_word_count <= 12:
        return "tight bullet pacing"

    return "slightly fuller explanatory pacing"


def _chunk_text(content: str, chunk_size: int = 48) -> list[str]:
    if not content:
        return []

    words = content.split()
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) > chunk_size and current:
            chunks.append(f"{current} ")
            current = word
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


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
