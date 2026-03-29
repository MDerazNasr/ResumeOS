import json
import uuid

from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.schemas import CompileLogEntryDto, CompileResultDto
from app.services.utils import utc_now_iso


def compile_resume_source_for_user(user_id: str, resume_id: str, source_tex: str, draft_version: int) -> CompileResultDto:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT d.version
            FROM working_drafts d
            JOIN resumes r ON r.id = d.resume_id
            WHERE d.resume_id = ? AND r.user_id = ?
            """,
            (resume_id, user_id),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

        current_version = row["version"]
        if current_version != draft_version:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Compile version conflict.")

    logs = _validate_source(source_tex)
    compile_status = "error" if any(log.level == "error" for log in logs) else "success"
    compiled_at = utc_now_iso()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO compile_runs (id, resume_id, draft_version, status, log_text, pdf_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"compile_{uuid.uuid4().hex[:12]}",
                resume_id,
                draft_version,
                compile_status,
                json.dumps([log.model_dump() for log in logs]),
                None,
                compiled_at,
            ),
        )
        connection.commit()

    return CompileResultDto(
        status=compile_status,
        draftVersion=draft_version,
        logs=logs,
        pdfUrl=None,
        compiledAt=compiled_at,
    )


def _validate_source(source_tex: str) -> list[CompileLogEntryDto]:
    logs: list[CompileLogEntryDto] = []
    lines = source_tex.splitlines()

    if "\\documentclass" not in source_tex:
        logs.append(CompileLogEntryDto(level="error", message="Missing \\documentclass declaration."))

    begin_line = _find_line(lines, "\\begin{document}")
    end_line = _find_line(lines, "\\end{document}")

    if begin_line is None:
        logs.append(CompileLogEntryDto(level="error", message="Missing \\begin{document}."))
    if end_line is None:
        logs.append(CompileLogEntryDto(level="error", message="Missing \\end{document}."))

    if begin_line is not None and end_line is not None and end_line < begin_line:
        logs.append(
            CompileLogEntryDto(
                level="error",
                message="\\end{document} appears before \\begin{document}.",
                line=end_line,
            )
        )

    if source_tex.count("{") != source_tex.count("}"):
        logs.append(CompileLogEntryDto(level="error", message="Unbalanced curly braces detected."))

    if not logs:
        logs.append(
            CompileLogEntryDto(
                level="info",
                message="Compile contract verified. Real TeX execution and PDF generation land in Section 2B.",
            )
        )

    return logs


def _find_line(lines: list[str], pattern: str) -> int | None:
    for index, line in enumerate(lines, start=1):
        if pattern in line:
            return index

    return None
