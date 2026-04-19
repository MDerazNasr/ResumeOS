import re
from pathlib import Path

from app.db.database import get_connection
from app.services.constraints import get_constraint_rules_for_user, has_one_line_bullet_rule
from app.models.schemas import HolisticReviewContextDto
from app.services.document_model import get_document_model_for_user
from app.services.resumes import get_draft_for_user


def get_holistic_review_context_for_user(user_id: str, resume_id: str) -> HolisticReviewContextDto:
    draft = get_draft_for_user(user_id, resume_id)
    document_model = get_document_model_for_user(user_id, resume_id)
    constraint_rules = get_constraint_rules_for_user(user_id, resume_id)

    with get_connection() as connection:
        latest_compile = connection.execute(
            """
            SELECT c.status, c.draft_version, c.created_at, c.pdf_path, c.log_text
            FROM compile_runs c
            JOIN resumes r ON r.id = c.resume_id
            WHERE c.resume_id = ? AND r.user_id = ?
            ORDER BY c.created_at DESC
            LIMIT 1
            """,
            (resume_id, user_id),
        ).fetchone()

    pdf_page_count = None
    pdf_size_kb = None
    layout_signals: list[str] = []

    if latest_compile and latest_compile["pdf_path"]:
        pdf_path = Path(latest_compile["pdf_path"])
        if pdf_path.exists():
            pdf_page_count = _extract_pdf_page_count(pdf_path)
            pdf_size_kb = max(1, round(pdf_path.stat().st_size / 1024))
            if pdf_page_count is not None:
                layout_signals.append("single-page-likely" if pdf_page_count <= 1 else "multi-page")
            else:
                layout_signals.append("page-count-unavailable")
            if pdf_size_kb >= 200:
                layout_signals.append("dense-pdf-artifact")

    if latest_compile and latest_compile["status"] == "error":
        layout_signals.append("compile-errors-present")

    rule_signals: list[str] = []
    likely_violation_labels: list[str] = []
    if has_one_line_bullet_rule(constraint_rules):
        rule_signals.append("one-line-bullet-rule-active")
        for block in document_model.editableBlocks:
            if block.kind == "bullet" and _likely_wraps_one_line(block.text):
                likely_violation_labels.append(block.label)
        if likely_violation_labels:
            rule_signals.append("likely-one-line-bullet-violations")

    return HolisticReviewContextDto(
        resumeId=resume_id,
        latestCompileStatus=latest_compile["status"] if latest_compile else None,
        latestCompileDraftVersion=latest_compile["draft_version"] if latest_compile else None,
        latestCompiledAt=latest_compile["created_at"] if latest_compile else None,
        pdfUrl=f"/resumes/{resume_id}/compile/latest.pdf" if latest_compile and latest_compile["pdf_path"] else None,
        pdfPageCount=pdf_page_count,
        pdfSizeKb=pdf_size_kb,
        layoutSignals=layout_signals,
        ruleSignals=rule_signals,
        likelyViolationLabels=likely_violation_labels[:6],
        sourceLineCount=len(draft.sourceTex.splitlines()),
        editableBlockCount=len(document_model.editableBlocks),
        editableBlockLabels=[block.label for block in document_model.editableBlocks[:5]],
    )


def _extract_pdf_page_count(pdf_path: Path) -> int | None:
    try:
        pdf_bytes = pdf_path.read_bytes()
    except OSError:
        return None

    matches = re.findall(rb"/Type\s*/Page\b", pdf_bytes)
    return len(matches) or None


def _likely_wraps_one_line(text: str) -> bool:
    compact = " ".join(text.split())
    return len(compact) > 95
