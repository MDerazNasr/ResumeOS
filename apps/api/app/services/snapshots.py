import sqlite3
import uuid

from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.schemas import (
    CreateSnapshotInput,
    SnapshotDetailDto,
    SnapshotDto,
    SnapshotListResponseDto,
    WorkingDraftDto,
)
from app.services.resumes import get_draft_for_user
from app.services.utils import utc_now_iso


def list_snapshots_for_user(user_id: str, resume_id: str) -> SnapshotListResponseDto:
    _ensure_resume_access(user_id, resume_id)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, resume_id, name, source_version, created_at
            FROM snapshots
            WHERE resume_id = ?
            ORDER BY created_at DESC
            """,
            (resume_id,),
        ).fetchall()

    return SnapshotListResponseDto(items=[_row_to_snapshot(row) for row in rows])


def create_snapshot_for_user(user_id: str, resume_id: str, input_data: CreateSnapshotInput) -> SnapshotDto:
    draft = get_draft_for_user(user_id, resume_id)
    return _create_snapshot_from_draft(resume_id, draft.sourceTex, draft.version, input_data.name.strip())


def create_automatic_snapshot_for_user(user_id: str, resume_id: str, name: str) -> SnapshotDto:
    draft = get_draft_for_user(user_id, resume_id)
    return _create_snapshot_from_draft(resume_id, draft.sourceTex, draft.version, name.strip())


def _create_snapshot_from_draft(resume_id: str, source_tex: str, source_version: int, name: str) -> SnapshotDto:
    snapshot_id = f"snap_{uuid.uuid4().hex[:12]}"
    created_at = utc_now_iso()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO snapshots (id, resume_id, name, source_tex, source_version, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                resume_id,
                name,
                source_tex,
                source_version,
                created_at,
            ),
        )
        connection.commit()

        row = connection.execute(
            """
            SELECT id, resume_id, name, source_version, created_at
            FROM snapshots
            WHERE id = ?
            """,
            (snapshot_id,),
        ).fetchone()

    return _row_to_snapshot(row)


def get_snapshot_for_user(user_id: str, resume_id: str, snapshot_id: str) -> SnapshotDetailDto:
    _ensure_resume_access(user_id, resume_id)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, resume_id, name, source_tex, source_version, created_at
            FROM snapshots
            WHERE id = ? AND resume_id = ?
            """,
            (snapshot_id, resume_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found.")

    return _row_to_snapshot_detail(row)


def restore_snapshot_for_user(user_id: str, resume_id: str, snapshot_id: str) -> WorkingDraftDto:
    _ensure_resume_access(user_id, resume_id)

    with get_connection() as connection:
        snapshot = connection.execute(
            """
            SELECT source_tex
            FROM snapshots
            WHERE id = ? AND resume_id = ?
            """,
            (snapshot_id, resume_id),
        ).fetchone()

        if snapshot is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found.")

        draft = connection.execute(
            """
            SELECT version
            FROM working_drafts
            WHERE resume_id = ?
            """,
            (resume_id,),
        ).fetchone()

        if draft is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

        next_version = draft["version"] + 1
        updated_at = utc_now_iso()

        connection.execute(
            """
            UPDATE working_drafts
            SET source_tex = ?, version = ?, updated_at = ?
            WHERE resume_id = ?
            """,
            (snapshot["source_tex"], next_version, updated_at, resume_id),
        )
        connection.execute(
            """
            UPDATE resumes
            SET updated_at = ?
            WHERE id = ?
            """,
            (updated_at, resume_id),
        )
        connection.commit()

    return get_draft_for_user(user_id, resume_id)


def _ensure_resume_access(user_id: str, resume_id: str) -> None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM resumes
            WHERE id = ? AND user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")


def _row_to_snapshot(row: sqlite3.Row) -> SnapshotDto:
    return SnapshotDto(
        id=row["id"],
        resumeId=row["resume_id"],
        name=row["name"],
        sourceVersion=row["source_version"],
        createdAt=row["created_at"],
    )


def _row_to_snapshot_detail(row: sqlite3.Row) -> SnapshotDetailDto:
    return SnapshotDetailDto(
        id=row["id"],
        resumeId=row["resume_id"],
        name=row["name"],
        sourceTex=row["source_tex"],
        sourceVersion=row["source_version"],
        createdAt=row["created_at"],
    )
