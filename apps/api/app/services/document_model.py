import re

from app.models.schemas import DocumentModelDto, EditableBlockDto, ProtectedRegionDto
from app.services.resumes import get_draft_for_user


SECTION_PATTERN = re.compile(r"\\section\*?\{([^}]*)\}")
BULLET_PATTERN = re.compile(r"^(\s*\\item\s+)(.+)$")
BEGIN_DOCUMENT = r"\begin{document}"
END_DOCUMENT = r"\end{document}"


def get_document_model_for_user(user_id: str, resume_id: str) -> DocumentModelDto:
    draft = get_draft_for_user(user_id, resume_id)
    return extract_document_model(resume_id, draft.sourceTex)


def extract_document_model(resume_id: str, source_tex: str) -> DocumentModelDto:
    lines = source_tex.split("\n")
    protected_regions: list[ProtectedRegionDto] = []
    editable_blocks: list[EditableBlockDto] = []

    begin_line = _find_line_number(lines, BEGIN_DOCUMENT)
    end_line = _find_line_number(lines, END_DOCUMENT)

    if begin_line > 1:
        protected_regions.append(
            ProtectedRegionDto(
                id="protected-preamble",
                kind="preamble",
                label="LaTeX preamble",
                startLine=1,
                endLine=begin_line - 1,
            )
        )

    if begin_line:
        protected_regions.append(
            ProtectedRegionDto(
                id="protected-begin-document",
                kind="scaffold",
                label=r"\begin{document}",
                startLine=begin_line,
                endLine=begin_line,
            )
        )

    if end_line:
        protected_regions.append(
            ProtectedRegionDto(
                id="protected-end-document",
                kind="scaffold",
                label=r"\end{document}",
                startLine=end_line,
                endLine=end_line,
            )
        )

    current_section = "Document body"
    body_start = begin_line + 1 if begin_line else 1
    body_end = end_line - 1 if end_line else len(lines)

    for index in range(body_start, body_end + 1):
        line = lines[index - 1]
        stripped = line.strip()

        if not stripped:
            continue

        section_match = SECTION_PATTERN.match(stripped)
        if section_match:
            current_section = section_match.group(1).strip() or "Untitled section"
            protected_regions.append(
                ProtectedRegionDto(
                    id=f"protected-section-{index}",
                    kind="command",
                    label=f"Section heading: {current_section}",
                    startLine=index,
                    endLine=index,
                )
            )
            continue

        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match:
            prefix, text = bullet_match.groups()
            editable_blocks.append(
                EditableBlockDto(
                    id=f"editable-bullet-{index}",
                    kind="bullet",
                    label=current_section,
                    text=text.rstrip(),
                    startLine=index,
                    startColumn=len(prefix) + 1,
                    endLine=index,
                    endColumn=len(line),
                )
            )
            continue

        if stripped.startswith("\\"):
            protected_regions.append(
                ProtectedRegionDto(
                    id=f"protected-command-{index}",
                    kind="command",
                    label=f"Command in {current_section}",
                    startLine=index,
                    endLine=index,
                )
            )
            continue

        start_column = len(line) - len(line.lstrip()) + 1
        editable_blocks.append(
            EditableBlockDto(
                id=f"editable-paragraph-{index}",
                kind="paragraph",
                label=current_section,
                text=stripped,
                startLine=index,
                startColumn=start_column,
                endLine=index,
                endColumn=len(line),
            )
        )

    return DocumentModelDto(
        resumeId=resume_id,
        protectedRegions=protected_regions,
        editableBlocks=editable_blocks,
    )


def _find_line_number(lines: list[str], target: str) -> int:
    for index, line in enumerate(lines, start=1):
        if target in line:
            return index

    return 0
