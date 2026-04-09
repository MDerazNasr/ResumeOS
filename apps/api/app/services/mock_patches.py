from app.models.schemas import PatchHunkDto, PatchSetDto, PatchSetListDto, ValidatePatchInput
from app.services.document_model import get_document_model_for_user
from app.services.patch_validation import validate_patch_for_user


def list_seeded_patch_sets_for_user(user_id: str, resume_id: str, seed: int = 0) -> PatchSetListDto:
    document_model = get_document_model_for_user(user_id, resume_id)
    editable_blocks = document_model.editableBlocks[:4]
    grouped_blocks = [editable_blocks[:2], editable_blocks[2:4]]
    suggestion_sets: list[PatchSetDto] = []

    for group_index, blocks in enumerate(grouped_blocks, start=1):
        proposals: list[PatchHunkDto] = []

        for index, block in enumerate(blocks, start=1):
            if block is None:
                continue

            after_text = _build_mock_after_text(block.kind, block.text, seed + group_index + index)
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
                PatchHunkDto(
                    id=f"mock-patch-{group_index}-{index}",
                    operation="replace",
                    status="validated",
                    targetBlockId=block.id,
                    label=block.label,
                    startLine=block.startLine,
                    endLine=block.endLine,
                    beforeText=block.text,
                    afterText=after_text,
                    rationale=_build_rationale(block.kind, seed + group_index),
                    validation=validation,
                )
            )

        if proposals:
            suggestion_sets.append(
                PatchSetDto(
                    id=f"mock-set-{group_index}",
                    mode="mock",
                    title=_build_set_title(group_index),
                    summary=_build_set_summary(group_index),
                    retrySeed=seed + 1,
                    items=proposals,
                )
            )

    return PatchSetListDto(items=suggestion_sets)


def _build_mock_after_text(block_kind: str, text: str, variant_seed: int) -> str:
    cleaned = text.rstrip(".")
    suffix = "measurable impact" if variant_seed % 2 == 0 else "sharper technical framing"
    if block_kind == "bullet":
        return f"{cleaned}, with clearer scope and {suffix}."

    return f"{cleaned} with sharper specificity and {suffix}."


def _build_rationale(block_kind: str, variant_seed: int) -> str:
    if block_kind == "bullet":
        if variant_seed % 2 == 0:
            return "This suggestion set emphasizes clearer outcomes and tighter execution language."

        return "This suggestion set leans toward stronger technical specificity in bullet wording."

    return "This suggestion set makes paragraph-level text more specific while preserving structure."


def _build_set_title(group_index: int) -> str:
    if group_index == 1:
        return "Core clarity pass"

    return "Experience and projects pass"


def _build_set_summary(group_index: int) -> str:
    if group_index == 1:
        return "Focuses on strengthening high-signal intro content and overall clarity."

    return "Focuses on making accomplishment-oriented content more explicit and technically sharp."
