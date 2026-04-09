from fastapi import HTTPException, status

from app.models.schemas import ApplyPatchInput, WorkingDraftDto
from app.services.document_model import get_document_model_for_user
from app.services.patch_validation import validate_patch_for_user
from app.services.resumes import get_draft_for_user, save_draft_for_user
from app.services.style_memory import store_accepted_style_example_for_user


def apply_patch_for_user(user_id: str, resume_id: str, input_data: ApplyPatchInput) -> WorkingDraftDto:
    validation = validate_patch_for_user(
        user_id,
        resume_id,
        input_data,
    )

    if not validation.isValid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=validation.reason or "Patch validation failed.",
        )

    draft = get_draft_for_user(user_id, resume_id)
    document_model = get_document_model_for_user(user_id, resume_id)
    target_block = next((block for block in document_model.editableBlocks if block.id == input_data.targetBlockId), None)

    if target_block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target block not found.")

    updated_source = _replace_block_text(draft.sourceTex, target_block, input_data.afterText)
    updated_draft = save_draft_for_user(user_id, resume_id, updated_source, draft.version)
    store_accepted_style_example_for_user(
        user_id,
        resume_id,
        block_kind=target_block.kind,
        block_label=target_block.label,
        text=input_data.afterText,
    )
    return updated_draft


def _replace_block_text(source_tex: str, target_block, replacement_text: str) -> str:
    lines = source_tex.split("\n")
    line_index = target_block.startLine - 1
    line = lines[line_index]

    prefix = line[: target_block.startColumn - 1]
    suffix = line[target_block.endColumn :]
    lines[line_index] = f"{prefix}{replacement_text}{suffix}"

    return "\n".join(lines)
