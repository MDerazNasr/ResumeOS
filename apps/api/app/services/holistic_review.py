from app.db.database import get_connection
from app.models.schemas import HolisticReviewContextDto
from app.services.document_model import get_document_model_for_user
from app.services.resumes import get_draft_for_user


def get_holistic_review_context_for_user(user_id: str, resume_id: str) -> HolisticReviewContextDto:
    draft = get_draft_for_user(user_id, resume_id)
    document_model = get_document_model_for_user(user_id, resume_id)

    with get_connection() as connection:
        latest_compile = connection.execute(
            """
            SELECT c.status, c.draft_version, c.created_at, c.pdf_path
            FROM compile_runs c
            JOIN resumes r ON r.id = c.resume_id
            WHERE c.resume_id = ? AND r.user_id = ?
            ORDER BY c.created_at DESC
            LIMIT 1
            """,
            (resume_id, user_id),
        ).fetchone()

    return HolisticReviewContextDto(
        resumeId=resume_id,
        latestCompileStatus=latest_compile["status"] if latest_compile else None,
        latestCompileDraftVersion=latest_compile["draft_version"] if latest_compile else None,
        latestCompiledAt=latest_compile["created_at"] if latest_compile else None,
        pdfUrl=f"/resumes/{resume_id}/compile/latest.pdf" if latest_compile and latest_compile["pdf_path"] else None,
        sourceLineCount=len(draft.sourceTex.splitlines()),
        editableBlockCount=len(document_model.editableBlocks),
        editableBlockLabels=[block.label for block in document_model.editableBlocks[:5]],
    )
