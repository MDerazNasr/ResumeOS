from app.models.schemas import PatchValidationResultDto, ValidatePatchInput
from app.services.document_model import get_document_model_for_user


def validate_patch_for_user(user_id: str, resume_id: str, input_data: ValidatePatchInput) -> PatchValidationResultDto:
    document_model = get_document_model_for_user(user_id, resume_id)
    target_block = next((block for block in document_model.editableBlocks if block.id == input_data.targetBlockId), None)

    if target_block is None:
        return PatchValidationResultDto(
            isValid=False,
            targetBlockId=input_data.targetBlockId,
            reason="Target block was not found in the current editable document model.",
        )

    if input_data.startLine != target_block.startLine or input_data.endLine != target_block.endLine:
        return PatchValidationResultDto(
            isValid=False,
            targetBlockId=input_data.targetBlockId,
            matchedCurrentText=target_block.text,
            reason="Proposed patch range does not exactly match the target editable block.",
        )

    if input_data.beforeText.strip() != target_block.text.strip():
        return PatchValidationResultDto(
            isValid=False,
            targetBlockId=input_data.targetBlockId,
            matchedCurrentText=target_block.text,
            reason="Proposed patch no longer matches the current draft text for that block.",
        )

    return PatchValidationResultDto(
        isValid=True,
        targetBlockId=input_data.targetBlockId,
        matchedCurrentText=target_block.text,
        reason=None,
    )
