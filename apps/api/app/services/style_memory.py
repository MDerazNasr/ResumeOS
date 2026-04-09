from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.db.database import get_connection
from app.services.document_model import get_document_model_for_user


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def refresh_draft_style_examples_for_user(user_id: str, resume_id: str) -> None:
    document_model = get_document_model_for_user(user_id, resume_id)
    now = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        _ensure_style_examples_table(connection)
        connection.execute(
            "DELETE FROM style_examples WHERE resume_id = ? AND source_type = ?",
            (resume_id, "draft"),
        )

        for block in document_model.editableBlocks:
            normalized = block.text.strip()
            if not normalized:
                continue

            connection.execute(
                """
                INSERT INTO style_examples (
                  id,
                  resume_id,
                  source_type,
                  block_kind,
                  block_label,
                  text,
                  created_at,
                  updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"style_{uuid4().hex}",
                    resume_id,
                    "draft",
                    block.kind,
                    block.label,
                    normalized,
                    now,
                    now,
                ),
            )

        connection.commit()


def get_relevant_style_examples_for_user(
    user_id: str,
    resume_id: str,
    *,
    instruction: str,
    target_text: str,
    preferred_kind: str | None = None,
    exclude_texts: set[str] | None = None,
    limit: int = 3,
) -> list[str]:
    refresh_draft_style_examples_for_user(user_id, resume_id)
    excluded = {text.strip() for text in (exclude_texts or set()) if text.strip()}
    target_tokens = _tokenize(f"{instruction} {target_text}")

    with get_connection() as connection:
        _ensure_style_examples_table(connection)
        rows = connection.execute(
            """
            SELECT block_kind, text
            FROM style_examples
            WHERE resume_id = ?
            """,
            (resume_id,),
        ).fetchall()

    scored_examples: list[tuple[int, int, str]] = []
    for row in rows:
        text = row["text"].strip()
        if not text or text in excluded:
            continue

        example_tokens = _tokenize(text)
        overlap = len(target_tokens & example_tokens)
        kind_bonus = 3 if preferred_kind and row["block_kind"] == preferred_kind else 0
        score = kind_bonus + overlap
        scored_examples.append((score, len(example_tokens), text))

    scored_examples.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [text for _, _, text in scored_examples[:limit]]


def _tokenize(text: str) -> set[str]:
    cleaned = "".join(character.lower() if character.isalnum() else " " for character in text)
    return {token for token in cleaned.split() if token and token not in _STOP_WORDS}


def _ensure_style_examples_table(connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS style_examples (
          id TEXT PRIMARY KEY,
          resume_id TEXT NOT NULL,
          source_type TEXT NOT NULL,
          block_kind TEXT NOT NULL,
          block_label TEXT NOT NULL,
          text TEXT NOT NULL,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          UNIQUE(resume_id, source_type, text)
        )
        """
    )
