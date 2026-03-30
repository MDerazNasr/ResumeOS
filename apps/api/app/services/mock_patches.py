from app.models.schemas import MockPatchProposalDto, MockPatchProposalListDto, ValidatePatchInput
from app.services.document_model import get_document_model_for_user
from app.services.patch_validation import validate_patch_for_user


def list_mock_patch_proposals_for_user(user_id: str, resume_id: str) -> MockPatchProposalListDto:
    document_model = get_document_model_for_user(user_id, resume_id)
    proposals: list[MockPatchProposalDto] = []

    for index, block in enumerate(document_model.editableBlocks[:3], start=1):
        after_text = _build_mock_after_text(block.kind, block.text)
        validation = validate_patch_for_user(
            user_id,
            resume_id,
            ValidatePatchInput(
                targetBlockId=block.id,
                startLine=block.startLine,
                endLine=block.endLine,
                beforeText=block.text,
            ),
        )

        if not validation.isValid:
            continue

        proposals.append(
            MockPatchProposalDto(
                id=f"mock-patch-{index}",
                targetBlockId=block.id,
                label=block.label,
                startLine=block.startLine,
                endLine=block.endLine,
                beforeText=block.text,
                afterText=after_text,
                rationale=_build_rationale(block.kind),
                validation=validation,
            )
        )

    return MockPatchProposalListDto(items=proposals)


def _build_mock_after_text(block_kind: str, text: str) -> str:
    cleaned = text.rstrip(".")
    if block_kind == "bullet":
        return f"{cleaned}, with clearer scope and measurable impact."

    return f"{cleaned} with sharper specificity and stronger technical framing."


def _build_rationale(block_kind: str) -> str:
    if block_kind == "bullet":
        return "This mocked patch tightens the bullet and adds more outcome-oriented phrasing."

    return "This mocked patch makes the paragraph more specific while preserving the existing structure."
