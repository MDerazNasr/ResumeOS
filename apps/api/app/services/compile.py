import json
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import FileResponse

from app.db.database import get_connection
from app.models.schemas import CompileLogEntryDto, CompileResultDto
from app.services.utils import utc_now_iso


ARTIFACTS_DIR = Path(__file__).resolve().parent.parent.parent / "artifacts"
COMPILE_TIMEOUT_SECONDS = 30


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

    compiled_at = utc_now_iso()
    pdf_path: str | None = None

    with tempfile.TemporaryDirectory(prefix="resumeos-compile-") as temp_dir:
        work_dir = Path(temp_dir)
        tex_path = work_dir / "resume.tex"
        tex_path.write_text(source_tex, encoding="utf-8")

        command = [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "resume.tex",
        ]

        try:
            completed = subprocess.run(
                command,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=COMPILE_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            logs = [
                CompileLogEntryDto(
                    level="error",
                    message=f"Compile timed out after {COMPILE_TIMEOUT_SECONDS} seconds.",
                )
            ]
            compile_status = "error"
        else:
            pdf_candidate = work_dir / "resume.pdf"
            raw_output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)

            if completed.returncode == 0 and pdf_candidate.exists():
                pdf_destination = _persist_pdf_artifact(resume_id, draft_version, pdf_candidate)
                pdf_path = str(pdf_destination)
                logs = [
                    CompileLogEntryDto(
                        level="info",
                        message="LaTeX compile completed successfully.",
                    )
                ]
                compile_status = "success"
            else:
                logs = _extract_compile_logs(raw_output)
                compile_status = "error"

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
                pdf_path,
                compiled_at,
            ),
        )
        connection.commit()

    return CompileResultDto(
        status=compile_status,
        draftVersion=draft_version,
        logs=logs,
        pdfUrl=f"/resumes/{resume_id}/compile/latest.pdf" if pdf_path else None,
        compiledAt=compiled_at,
    )


def get_latest_pdf_for_user(user_id: str, resume_id: str) -> FileResponse:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT c.pdf_path
            FROM compile_runs c
            JOIN resumes r ON r.id = c.resume_id
            WHERE c.resume_id = ? AND r.user_id = ? AND c.status = 'success' AND c.pdf_path IS NOT NULL
            ORDER BY c.created_at DESC
            LIMIT 1
            """,
            (resume_id, user_id),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compiled PDF not found.")

    pdf_path = Path(row["pdf_path"])
    if not pdf_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compiled PDF artifact missing.")

    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.name)


def _persist_pdf_artifact(resume_id: str, draft_version: int, pdf_candidate: Path) -> Path:
    destination_dir = ARTIFACTS_DIR / resume_id
    destination_dir.mkdir(parents=True, exist_ok=True)

    latest_destination = destination_dir / "latest.pdf"
    versioned_destination = destination_dir / f"draft-v{draft_version}.pdf"

    shutil.copy2(pdf_candidate, versioned_destination)
    shutil.copy2(pdf_candidate, latest_destination)

    return latest_destination


def _extract_compile_logs(raw_output: str) -> list[CompileLogEntryDto]:
    if not raw_output.strip():
        return [CompileLogEntryDto(level="error", message="Compile failed without output.")]

    lines = [line.strip() for line in raw_output.splitlines() if line.strip()]
    error_lines: list[CompileLogEntryDto] = []

    for index, line in enumerate(lines):
        if line.startswith("!"):
            error_lines.append(
                CompileLogEntryDto(
                    level="error",
                    message=line.lstrip("! ").strip(),
                    line=_extract_line_number(lines, index),
                )
            )

    if error_lines:
        return error_lines[:5]

    tail = "\n".join(lines[-10:])
    return [CompileLogEntryDto(level="error", message=tail)]


def _extract_line_number(lines: list[str], current_index: int) -> int | None:
    pattern = re.compile(r"l\.(\d+)")

    for offset in range(current_index, min(current_index + 4, len(lines))):
        match = pattern.search(lines[offset])
        if match:
            return int(match.group(1))

    return None
