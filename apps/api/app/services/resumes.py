import sqlite3
import uuid

from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.schemas import CreateResumeInput, ResumeDto, ResumeListResponseDto, WorkingDraftDto
from app.services.templates import load_starter_resume
from app.services.utils import slugify, utc_now_iso


def ensure_dev_user_exists(user_id: str, email: str, name: str) -> None:
    timestamp = utc_now_iso()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (id, email, name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET email = excluded.email, name = excluded.name, updated_at = excluded.updated_at
            """,
            (user_id, email, name, timestamp, timestamp),
        )
        connection.commit()


def list_resumes_for_user(user_id: str) -> ResumeListResponseDto:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, slug, status, created_at, updated_at
            FROM resumes
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (user_id,),
        ).fetchall()

    return ResumeListResponseDto(items=[_row_to_resume(row) for row in rows])


def create_resume_for_user(user_id: str, input_data: CreateResumeInput) -> ResumeDto:
    resume_id = f"res_{uuid.uuid4().hex[:12]}"
    draft_id = f"draft_{uuid.uuid4().hex[:12]}"
    timestamp = utc_now_iso()
    slug = _next_available_slug(user_id, slugify(input_data.title))

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO resumes (id, user_id, title, slug, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
            """,
            (resume_id, user_id, input_data.title.strip(), slug, timestamp, timestamp),
        )
        connection.execute(
            """
            INSERT INTO working_drafts (id, resume_id, source_tex, version, updated_at)
            VALUES (?, ?, ?, 1, ?)
            """,
            (draft_id, resume_id, load_starter_resume(), timestamp),
        )
        connection.commit()

        row = connection.execute(
            """
            SELECT id, title, slug, status, created_at, updated_at
            FROM resumes
            WHERE id = ? AND user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

    return _row_to_resume(row)


def get_resume_for_user(user_id: str, resume_id: str) -> ResumeDto:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, slug, status, created_at, updated_at
            FROM resumes
            WHERE id = ? AND user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    return _row_to_resume(row)


def get_draft_for_user(user_id: str, resume_id: str) -> WorkingDraftDto:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT d.resume_id, d.source_tex, d.version, d.updated_at
            FROM working_drafts d
            JOIN resumes r ON r.id = d.resume_id
            WHERE d.resume_id = ? AND r.user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

    return WorkingDraftDto(
        resumeId=row["resume_id"],
        sourceTex=row["source_tex"],
        version=row["version"],
        updatedAt=row["updated_at"],
    )


def save_draft_for_user(user_id: str, resume_id: str, source_tex: str, version: int) -> WorkingDraftDto:
    timestamp = utc_now_iso()

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT d.version
            FROM working_drafts d
            JOIN resumes r ON r.id = d.resume_id
            WHERE d.resume_id = ? AND r.user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

        current_version = existing["version"]
        if version != current_version:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft version conflict.")

        next_version = current_version + 1
        connection.execute(
            """
            UPDATE working_drafts
            SET source_tex = ?, version = ?, updated_at = ?
            WHERE resume_id = ?
            """,
            (source_tex, next_version, timestamp, resume_id),
        )
        connection.execute(
            """
            UPDATE resumes
            SET updated_at = ?
            WHERE id = ?
            """,
            (timestamp, resume_id),
        )
        connection.commit()

    return get_draft_for_user(user_id, resume_id)


def _next_available_slug(user_id: str, base_slug: str) -> str:
    candidate = base_slug
    counter = 2

    with get_connection() as connection:
        while True:
            existing = connection.execute(
                """
                SELECT 1
                FROM resumes
                WHERE user_id = ? AND slug = ?
                """,
                (user_id, candidate),
            ).fetchone()
            if existing is None:
                return candidate

            candidate = f"{base_slug}-{counter}"
            counter += 1


def _row_to_resume(row: sqlite3.Row) -> ResumeDto:
    return ResumeDto(
        id=row["id"],
        title=row["title"],
        slug=row["slug"],
        status=row["status"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )

