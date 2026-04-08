from fastapi import HTTPException, status

from app.models.schemas import GenerateEditSuggestionsInput, MockPatchProposalDto, MockSuggestionSetDto, MockSuggestionSetListDto, ValidatePatchInput
from app.services.document_model import get_document_model_for_user
from app.services.llm_provider import EditSuggestionPrompt, get_edit_suggestion_provider
from app.services.patch_validation import validate_patch_for_user


def generate_edit_suggestions_for_user(
    user_id: str,
    resume_id: str,
    input_data: GenerateEditSuggestionsInput,
) -> MockSuggestionSetListDto:
    document_model = get_document_model_for_user(user_id, resume_id)
    target_block = next((block for block in document_model.editableBlocks if block.id == input_data.targetBlockId), None)

    if target_block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target editable block not found.")

    provider = get_edit_suggestion_provider()
    candidates = provider.generate_rewrites(
        EditSuggestionPrompt(
            block_kind=target_block.kind,
            block_label=target_block.label,
            instruction=input_data.instruction,
            text=target_block.text,
        )
    )

    proposals: list[MockPatchProposalDto] = []
    for index, after_text in enumerate(candidates, start=1):
        validation = validate_patch_for_user(
            user_id,
            resume_id,
            ValidatePatchInput(
                targetBlockId=target_block.id,
                startLine=target_block.startLine,
                endLine=target_block.endLine,
                beforeText=target_block.text,
            ),
        )

        if not validation.isValid:
            continue

        proposals.append(
            MockPatchProposalDto(
                id=f"generated-edit-{index}",
                operation="replace",
                status="validated",
                targetBlockId=target_block.id,
                label=target_block.label,
                startLine=target_block.startLine,
                endLine=target_block.endLine,
                beforeText=target_block.text,
                afterText=after_text,
                rationale=f'Generated from instruction: "{input_data.instruction}"',
                validation=validation,
            )
        )

    return MockSuggestionSetListDto(
        items=[
            MockSuggestionSetDto(
                id=f"generated-set-{target_block.id}",
                title=f"Edit suggestions for {target_block.label}",
                summary=input_data.instruction,
                retrySeed=0,
                items=proposals,
            )
        ]
    )
