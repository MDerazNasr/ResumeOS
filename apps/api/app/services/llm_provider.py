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
    constraints: list[str]


@dataclass
class ReviewSuggestionPrompt:
    instruction: str
    blocks: list[EditSuggestionPrompt]
    holistic_context: str | None = None


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
    resume_context_snippets: list[str]
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
        constraint_suffix = _constraint_suffix(prompt.constraints)
        base_suffix = f"clearer scope, stronger technical specificity, and {style_tone}"
        alternate_suffix = f"more direct impact framing while preserving the user's {style_tone}"

        if prompt.block_kind == "bullet":
            return [
                f"{cleaned}, with {base_suffix}{constraint_suffix}.",
                f"{cleaned}, with {alternate_suffix}{constraint_suffix}.",
            ]

        return [
            f"{cleaned} with {base_suffix}{constraint_suffix}.",
            f"{cleaned} with {alternate_suffix}{constraint_suffix}.",
        ]

    def generate_review_rewrites(self, prompt: ReviewSuggestionPrompt) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}

        for block in prompt.blocks:
            review_instruction = prompt.instruction
            if prompt.holistic_context:
                review_instruction = f"{prompt.instruction} Holistic context: {prompt.holistic_context}"

            result[block.text] = self.generate_rewrites(
                EditSuggestionPrompt(
                    block_kind=block.block_kind,
                    block_label=block.block_label,
                    instruction=review_instruction,
                    text=block.text,
                    style_examples=block.style_examples,
                    constraints=block.constraints,
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
        style_hint = prompt.style_examples[0] if prompt.style_examples else None
        context_hint = prompt.resume_context_snippets[0] if prompt.resume_context_snippets else "No specific resume excerpt was available."
        follow_up_hint = " I'm treating this as a follow-up to the recent conversation." if prompt.intent_source == "history" else ""
        feedback_hint = f" Recent accepted/rejected edits: {prompt.recent_feedback_summary}." if prompt.recent_feedback_summary else ""
        if prompt.detected_intent == "question":
            return (
                f"Looking at the resume, one relevant part is: \"{context_hint}\".{follow_up_hint}"
                f"{f' A related style pattern is: \"{style_hint}\".' if style_hint else ''}"
                f"{feedback_hint} Ask me to review, tailor, or rewrite something if you want concrete edits."
            )

        if prompt.detected_intent == "review":
            return (
                f"I reviewed the resume and focused on places like \"{context_hint}\". "
                f"{prompt.patch_set_summary or 'I could not produce valid review edits this time.'}"
                f"{follow_up_hint}{feedback_hint} Read through the edits inline and keep only the ones that improve clarity."
            )

        if prompt.detected_intent == "tailor":
            return (
                f"I tailored the resume toward the role and used blocks like \"{context_hint}\" as starting points. "
                f"{prompt.patch_set_summary or 'I could not produce valid tailoring edits this time.'}"
                f"{follow_up_hint}{feedback_hint} Review the changes inline and keep the ones that genuinely match the job."
            )

        return (
            f"I drafted edits around text like \"{context_hint}\". "
            f"{prompt.patch_set_summary or 'I could not produce valid edit suggestions this time.'}"
            f"{follow_up_hint}{feedback_hint} Review the edits inline before applying them."
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
                            f"Constraints: {json.dumps(prompt.constraints)}\n"
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
                                "holistic_context": prompt.holistic_context,
                                "blocks": [
                                    {
                                        "label": block.block_label,
                                        "kind": block.block_kind,
                                        "text": block.text,
                                        "style_examples": block.style_examples,
                                        "constraints": block.constraints,
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
                                        "constraints": block.constraints,
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
                            "You are an AI resume collaborator inside an editor. "
                            "Sound natural, direct, and conversational, not like a system status readout. "
                            "Use the recent conversation and the provided resume snippets to answer like you are actively helping the user improve the resume. "
                            "Do not say phrases like 'I read that as' or narrate internal routing. "
                            "If edits were generated, mention them naturally and briefly tell the user what changed. "
                            "Leave patch counts, badges, and workflow mechanics to the UI unless they are directly helpful."
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
                                "resume_context_snippets": prompt.resume_context_snippets,
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
                            "You are an AI resume collaborator inside an editor. "
                            "Sound natural, direct, and conversational, not like a system status readout. "
                            "Use the recent conversation and the provided resume snippets to answer like you are actively helping the user improve the resume. "
                            "Do not say phrases like 'I read that as' or narrate internal routing. "
                            "If edits were generated, mention them naturally and briefly tell the user what changed. "
                            "Leave patch counts, badges, and workflow mechanics to the UI unless they are directly helpful."
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
                                "resume_context_snippets": prompt.resume_context_snippets,
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


def _constraint_suffix(constraints: list[str]) -> str:
    if not constraints:
        return ""
    return f", while following constraints such as {constraints[0].rstrip('.')}"


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

    if provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("RESUMEOS_GEMINI_MODEL", "gemini-2.5-flash")
        base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required when RESUMEOS_LLM_PROVIDER=gemini.")

        return OpenAIEditSuggestionProvider(api_key=api_key, model=model, base_url=base_url)

    return MockEditSuggestionProvider()
