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


def store_accepted_style_example_for_user(
    user_id: str,
    resume_id: str,
    *,
    block_kind: str,
    block_label: str,
    text: str,
) -> None:
    normalized = text.strip()
    if not normalized:
        return

    now = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        _ensure_style_examples_table(connection)
        resume = connection.execute(
            """
            SELECT 1
            FROM resumes
            WHERE id = ? AND user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

        if resume is None:
            return

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
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(resume_id, source_type, text)
            DO UPDATE SET
              block_kind = excluded.block_kind,
              block_label = excluded.block_label,
              updated_at = excluded.updated_at
            """,
            (
                f"style_{uuid4().hex}",
                resume_id,
                "accepted",
                block_kind,
                block_label,
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
            SELECT block_kind, block_label, text, updated_at
                 , source_type
            FROM style_examples
            WHERE resume_id = ?
            """,
            (resume_id,),
        ).fetchall()

    scored_examples: list[tuple[int, int, str, int, str, str]] = []
    for row in rows:
        text = row["text"].strip()
        if not text or text in excluded:
            continue

        example_tokens = _tokenize(text)
        overlap = len(target_tokens & example_tokens)
        kind_bonus = 3 if preferred_kind and row["block_kind"] == preferred_kind else 0
        source_bonus = 5 if row["source_type"] == "accepted" else 0
        score = source_bonus + kind_bonus + overlap
        scored_examples.append(
            (
                score,
                source_bonus,
                row["updated_at"],
                len(example_tokens),
                row["block_label"],
                text,
            )
        )

    scored_examples.sort(key=lambda item: (-item[0], -item[1], item[2], item[3], item[5]), reverse=False)
    return _select_diverse_examples(scored_examples, limit)


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


def _select_diverse_examples(
    scored_examples: list[tuple[int, int, str, int, str, str]],
    limit: int,
) -> list[str]:
    selected: list[str] = []
    used_labels: set[str] = set()
    remaining = sorted(
        scored_examples,
        key=lambda item: (-item[0], -item[1], -_updated_at_rank(item[2]), item[3], item[5]),
    )

    for score, source_bonus, updated_at, token_length, block_label, text in remaining:
        if len(selected) >= limit:
            break
        if block_label in used_labels:
            continue

        selected.append(text)
        used_labels.add(block_label)

    if len(selected) >= limit:
        return selected

    for _, _, _, _, _, text in remaining:
        if len(selected) >= limit:
            break
        if text in selected:
            continue
        selected.append(text)

    return selected


def _updated_at_rank(updated_at: str) -> float:
    try:
        return datetime.fromisoformat(updated_at).timestamp()
    except ValueError:
        return 0.0
