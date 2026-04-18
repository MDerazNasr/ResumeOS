import json
import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from collections.abc import AsyncIterator

from app.db.database import get_connection
from app.models.schemas import ChatMessageDto, ChatResponseDto, ChatThreadDto, CreateChatMessageInput, GenerateReviewSuggestionsInput, GenerateTailorSuggestionsInput, PatchSetDto
from app.services.document_model import get_document_model_for_user
from app.services.edit_suggestions import generate_review_suggestions_for_user, generate_tailor_suggestions_for_user
from app.services.llm_provider import ChatConversationPrompt, get_edit_suggestion_provider
from app.services.resumes import get_draft_for_user
from app.services.resumes import get_resume_for_user
from app.services.style_memory import get_relevant_style_examples_for_user

ChatIntent = str


@dataclass
class ResolvedChatIntent:
    intent: ChatIntent
    source: str
    referencedUserMessage: str | None = None


def ensure_chat_schema() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_threads (
              id TEXT PRIMARY KEY,
              resume_id TEXT NOT NULL UNIQUE,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              FOREIGN KEY(resume_id) REFERENCES resumes(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
              id TEXT PRIMARY KEY,
              thread_id TEXT NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(thread_id) REFERENCES chat_threads(id)
            )
            """
        )
        connection.commit()


def get_chat_thread_for_user(user_id: str, resume_id: str) -> ChatThreadDto:
    ensure_chat_schema()
    get_resume_for_user(user_id, resume_id)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, resume_id, created_at, updated_at
            FROM chat_threads
            WHERE resume_id = ?
            """,
            (resume_id,),
        ).fetchone()

        if row is None:
            now = _now_iso()
            thread_id = f"thread_{uuid.uuid4().hex[:12]}"
            connection.execute(
                """
                INSERT INTO chat_threads (id, resume_id, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (thread_id, resume_id, now, now),
            )
            connection.commit()
            row = connection.execute(
                """
                SELECT id, resume_id, created_at, updated_at
                FROM chat_threads
                WHERE id = ?
                """,
                (thread_id,),
            ).fetchone()

        return ChatThreadDto(
            id=row["id"],
            resumeId=row["resume_id"],
            messages=_list_thread_messages(connection, row["id"]),
        )


def create_chat_message_for_user(user_id: str, resume_id: str, input_data: CreateChatMessageInput) -> ChatResponseDto:
    return _create_chat_response_for_user(user_id, resume_id, input_data)


async def stream_chat_message_for_user(user_id: str, resume_id: str, input_data: CreateChatMessageInput) -> AsyncIterator[str]:
    ensure_chat_schema()
    thread = get_chat_thread_for_user(user_id, resume_id)
    user_content = input_data.content.strip()
    resolved_intent = _resolve_chat_intent(user_content, thread.messages)
    patch_sets = _build_chat_patch_sets(user_id, resume_id, user_content, resolved_intent)
    factual_answer = _build_factual_question_answer(user_id, resume_id, user_content, resolved_intent.intent)
    prompt = _build_chat_prompt(user_id, resume_id, user_content, resolved_intent, patch_sets, thread.messages)
    provider = get_edit_suggestion_provider()
    assistant_chunks: list[str] = []

    yield _encode_stream_event(
        "start",
        {
            "chatIntent": resolved_intent.intent,
            "intentSource": resolved_intent.source,
        },
    )

    stream_source = _chunk_text(factual_answer) if factual_answer is not None else provider.stream_chat_reply(prompt)

    for chunk in stream_source:
        assistant_chunks.append(chunk)
        yield _encode_stream_event("delta", {"delta": chunk})

    response = _persist_chat_response(
        resume_id=resume_id,
        thread_id=thread.id,
        user_content=user_content,
        assistant_content="".join(assistant_chunks).strip(),
        resolved_intent=resolved_intent,
        patch_sets=patch_sets,
    )

    yield _encode_stream_event(
        "complete",
        {
            "response": response.model_dump(),
        },
    )


def _create_chat_response_for_user(user_id: str, resume_id: str, input_data: CreateChatMessageInput) -> ChatResponseDto:
    ensure_chat_schema()
    thread = get_chat_thread_for_user(user_id, resume_id)
    user_content = input_data.content.strip()
    resolved_intent = _resolve_chat_intent(user_content, thread.messages)
    patch_sets = _build_chat_patch_sets(user_id, resume_id, user_content, resolved_intent)
    factual_answer = _build_factual_question_answer(user_id, resume_id, user_content, resolved_intent.intent)
    if factual_answer is not None:
        assistant_content = factual_answer
    else:
        prompt = _build_chat_prompt(user_id, resume_id, user_content, resolved_intent, patch_sets, thread.messages)
        assistant_content = get_edit_suggestion_provider().generate_chat_reply(prompt)

    return _persist_chat_response(
        resume_id=resume_id,
        thread_id=thread.id,
        user_content=user_content,
        assistant_content=assistant_content,
        resolved_intent=resolved_intent,
        patch_sets=patch_sets,
    )


def _persist_chat_response(
    *,
    resume_id: str,
    thread_id: str,
    user_content: str,
    assistant_content: str,
    resolved_intent: ResolvedChatIntent,
    patch_sets: list[PatchSetDto],
) -> ChatResponseDto:
    assistant_content = assistant_content.strip() or "I wasn't able to generate a response for that request."
    with get_connection() as connection:
        now = _now_iso()
        user_message_id = f"msg_{uuid.uuid4().hex[:12]}"
        assistant_message_id = f"msg_{uuid.uuid4().hex[:12]}"
        connection.execute(
            """
            INSERT INTO chat_messages (id, thread_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_message_id, thread_id, "user", user_content, now),
        )
        connection.execute(
            """
            INSERT INTO chat_messages (id, thread_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (assistant_message_id, thread_id, "assistant", assistant_content, now),
        )
        connection.execute(
            "UPDATE chat_threads SET updated_at = ? WHERE id = ?",
            (now, thread_id),
        )
        connection.commit()

        updated_messages = _list_thread_messages(connection, thread_id)

    return ChatResponseDto(
        thread=ChatThreadDto(id=thread_id, resumeId=resume_id, messages=updated_messages),
        chatIntent=resolved_intent.intent,
        intentSource=resolved_intent.source,
        generatedPatchSetSummary=_build_patch_set_summary(resolved_intent.intent, patch_sets),
        recentFeedbackSummary=_get_recent_feedback_summary_for_resume(resume_id),
        assistantMessageId=assistant_message_id,
        patchSets=patch_sets,
    )


def _build_chat_patch_sets(user_id: str, resume_id: str, content: str, resolved_intent: ResolvedChatIntent) -> list[PatchSetDto]:
    if resolved_intent.intent == "tailor":
        job_description = content if resolved_intent.source == "message" else resolved_intent.referencedUserMessage
        if job_description and len(job_description) >= 40:
            instruction = (
                "Tailor the resume toward the intent in this chat request."
                if resolved_intent.source == "message"
                else content[:300]
            )
            return generate_tailor_suggestions_for_user(
                user_id,
                resume_id,
                GenerateTailorSuggestionsInput(
                    jobDescription=job_description,
                    instruction=instruction,
                ),
            ).items

    if resolved_intent.intent in {"review", "edit"}:
        return generate_review_suggestions_for_user(
            user_id,
            resume_id,
            GenerateReviewSuggestionsInput(
                instruction=content[:300],
            ),
        ).items

    return []


def _build_chat_prompt(
    user_id: str,
    resume_id: str,
    content: str,
    resolved_intent: ResolvedChatIntent,
    patch_sets: list[PatchSetDto],
    thread_messages: list[ChatMessageDto],
) -> ChatConversationPrompt:
    document_model = get_document_model_for_user(user_id, resume_id)
    style_examples = get_relevant_style_examples_for_user(
        user_id,
        resume_id,
        instruction=content,
        target_text=content,
        preferred_kind="bullet",
    )
    return ChatConversationPrompt(
        user_message=content,
        detected_intent=resolved_intent.intent,
        intent_source=resolved_intent.source,
        recent_messages=_recent_messages_for_thread(thread_messages),
        editable_block_count=len(document_model.editableBlocks),
        resume_context_snippets=_build_resume_context_snippets(document_model.editableBlocks),
        style_examples=style_examples,
        patch_set_summary=_build_patch_set_summary(resolved_intent.intent, patch_sets),
        recent_feedback_summary=_get_recent_feedback_summary_for_resume(resume_id),
    )


def _resolve_chat_intent(content: str, messages: list[ChatMessageDto]) -> ResolvedChatIntent:
    direct_intent = _classify_chat_intent(content)
    if direct_intent != "question":
        return ResolvedChatIntent(intent=direct_intent, source="message")

    if _looks_like_follow_up(content):
        last_actionable_message = _find_last_actionable_user_message(messages)
        if last_actionable_message is not None:
            return ResolvedChatIntent(
                intent=last_actionable_message[0],
                source="history",
                referencedUserMessage=last_actionable_message[1],
            )

    return ResolvedChatIntent(intent="question", source="message")


def _classify_chat_intent(content: str) -> ChatIntent:
    lowered = content.lower()

    if any(term in lowered for term in ["tailor", "job description", "jd", "role requirements"]):
        return "tailor"

    if any(term in lowered for term in ["review", "critique", "feedback", "assess"]):
        return "review"

    if any(term in lowered for term in ["rewrite", "improve", "reword", "shorten", "strengthen", "tighten"]):
        return "edit"

    return "question"


def _looks_like_follow_up(content: str) -> bool:
    lowered = content.lower().strip()
    if not lowered or len(lowered) > 240:
        return False

    follow_up_markers = [
        "and ",
        "also",
        "instead",
        "more ",
        "shorter",
        "stronger",
        "focus",
        "emphasize",
        "highlight",
        "tighten",
        "can you",
        "what about",
        "do the same",
        "make it",
        "make them",
        "those",
        "them",
    ]
    return any(marker in lowered for marker in follow_up_markers)


def _find_last_actionable_user_message(messages: list[ChatMessageDto]) -> tuple[ChatIntent, str] | None:
    for message in reversed(messages):
        if message.role != "user":
            continue

        intent = _classify_chat_intent(message.content)
        if intent != "question":
            return intent, message.content

    return None


def _build_patch_set_summary(chat_intent: ChatIntent, patch_sets: list[PatchSetDto]) -> str | None:
    if not patch_sets:
        return None

    hunk_count = sum(len(patch_set.items) for patch_set in patch_sets)
    return (
        f"{chat_intent.title()} response loaded {len(patch_sets)} patch set"
        f"{'' if len(patch_sets) == 1 else 's'} with {hunk_count} hunk{'' if hunk_count == 1 else 's'}."
    )


def _list_thread_messages(connection, thread_id: str) -> list[ChatMessageDto]:
    rows = connection.execute(
        """
        SELECT id, role, content, created_at
        FROM chat_messages
        WHERE thread_id = ?
        ORDER BY rowid ASC
        """,
        (thread_id,),
    ).fetchall()
    return [
        ChatMessageDto(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            createdAt=row["created_at"],
        )
        for row in rows
    ]


def _recent_messages_for_thread(messages: list[ChatMessageDto], limit: int = 6) -> list[tuple[str, str]]:
    if not messages:
        return []

    recent = messages[-limit:]
    return [(message.role, message.content) for message in recent]


def _encode_stream_event(event_type: str, payload: dict) -> str:
    return json.dumps({"type": event_type, **payload}) + "\n"


def _get_recent_feedback_summary_for_resume(resume_id: str) -> str | None:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT action, suggestion_mode, COUNT(*) AS count
            FROM feedback_events
            WHERE resume_id = ?
            GROUP BY action, suggestion_mode
            ORDER BY MAX(created_at) DESC
            LIMIT 4
            """,
            (resume_id,),
        ).fetchall()

    if not rows:
        return None

    parts = [f"{row['count']} {row['action']} {row['suggestion_mode']}" for row in rows]
    return ", ".join(parts)


def _build_factual_question_answer(user_id: str, resume_id: str, content: str, chat_intent: ChatIntent) -> str | None:
    if chat_intent != "question":
        return None

    extracted_term = _extract_count_query_term(content)
    if extracted_term is None:
        return None

    draft = get_draft_for_user(user_id, resume_id)
    count = _count_occurrences(draft.sourceTex, extracted_term)
    normalized_term = extracted_term.strip()
    quoted_term = normalized_term if normalized_term.startswith("\"") else normalized_term
    match_word = "time" if count == 1 else "times"
    return f'"{quoted_term}" appears {count} {match_word} in the current LaTeX resume source.'


def _extract_count_query_term(content: str) -> str | None:
    lowered = content.lower()
    if not any(marker in lowered for marker in ["how many times", "how often", "count", "mentions"]):
        return None

    quoted_match = re.search(r'"([^"]+)"|\'([^\']+)\'', content)
    if quoted_match:
        return quoted_match.group(1) or quoted_match.group(2)

    patterns = [
        r"how many times does\s+(.+?)\s+(?:show up|appear|occur|exist|appear in|show up in)",
        r"how many times is\s+(.+?)\s+(?:used|mentioned|listed)",
        r"count\s+(.+?)\s+(?:in|on)\s+(?:my|the)\s+resume",
        r"how many\s+(.+?)\s+mentions",
    ]
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return content[match.start(1):match.end(1)].strip(" ?.")

    return None


def _count_occurrences(source_text: str, term: str) -> int:
    normalized_source = source_text.lower()
    normalized_term = term.lower().strip()
    if not normalized_term:
        return 0
    return normalized_source.count(normalized_term)


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


def _build_resume_context_snippets(editable_blocks, limit: int = 4) -> list[str]:
    snippets: list[str] = []
    for block in editable_blocks[:limit]:
        snippets.append(f"{block.label}: {block.text}")
    return snippets


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
