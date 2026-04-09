import uuid

from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.schemas import LogFeedbackInput
from app.services.utils import utc_now_iso


def log_feedback_for_user(user_id: str, resume_id: str, input_data: LogFeedbackInput) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_events (
              id TEXT PRIMARY KEY,
              resume_id TEXT NOT NULL,
              suggestion_mode TEXT NOT NULL,
              action TEXT NOT NULL,
              suggestion_set_id TEXT NOT NULL,
              proposal_id TEXT NOT NULL,
              target_block_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY(resume_id) REFERENCES resumes(id)
            )
            """
        )
        resume = connection.execute(
            """
            SELECT 1
            FROM resumes
            WHERE id = ? AND user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

        if resume is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

        connection.execute(
            """
            INSERT INTO feedback_events (
              id,
              resume_id,
              suggestion_mode,
              action,
              suggestion_set_id,
              proposal_id,
              target_block_id,
              created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"fb_{uuid.uuid4().hex[:12]}",
                resume_id,
                input_data.suggestionMode,
                input_data.action,
                input_data.suggestionSetId,
                input_data.proposalId,
                input_data.targetBlockId,
                utc_now_iso(),
            ),
        )
        connection.commit()
