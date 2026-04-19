from fastapi import HTTPException, status

from app.models.schemas import GenerateEditSuggestionsInput, GenerateHolisticReviewSuggestionsInput, GenerateReviewSuggestionsInput, GenerateTailorSuggestionsInput, PatchHunkDto, PatchSetDto, PatchSetListDto, ValidatePatchInput
from app.services.constraints import get_constraint_rules_for_user
from app.services.document_model import get_document_model_for_user
from app.services.holistic_review import get_holistic_review_context_for_user
from app.services.llm_provider import EditSuggestionPrompt, ReviewSuggestionPrompt, TailorSuggestionPrompt, get_edit_suggestion_provider
from app.services.patch_validation import validate_patch_for_user
from app.services.snapshots import create_automatic_snapshot_for_user
from app.services.style_memory import get_relevant_style_examples_for_user


def generate_edit_suggestions_for_user(
    user_id: str,
    resume_id: str,
    input_data: GenerateEditSuggestionsInput,
) -> PatchSetListDto:
    document_model = get_document_model_for_user(user_id, resume_id)
    target_block = next((block for block in document_model.editableBlocks if block.id == input_data.targetBlockId), None)
    constraint_rules = get_constraint_rules_for_user(user_id, resume_id)

    if target_block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target editable block not found.")

    provider = get_edit_suggestion_provider()
    style_examples = get_relevant_style_examples_for_user(
        user_id,
        resume_id,
        instruction=input_data.instruction,
        target_text=target_block.text,
        preferred_kind=target_block.kind,
        exclude_texts={target_block.text},
    )
    candidates = provider.generate_rewrites(
        EditSuggestionPrompt(
            block_kind=target_block.kind,
            block_label=target_block.label,
            instruction=input_data.instruction,
            text=target_block.text,
            style_examples=style_examples,
            constraints=constraint_rules,
        )
    )

    proposals: list[PatchHunkDto] = []
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
            PatchHunkDto(
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

    return PatchSetListDto(
        items=[
            PatchSetDto(
                id=f"generated-set-{target_block.id}",
                mode="edit",
                title=f"Edit suggestions for {target_block.label}",
                summary=input_data.instruction,
                styleExamples=style_examples,
                retrySeed=0,
                items=proposals,
            )
        ]
    )


def generate_review_suggestions_for_user(
    user_id: str,
    resume_id: str,
    input_data: GenerateReviewSuggestionsInput,
) -> PatchSetListDto:
    return _generate_review_suggestions_for_user(user_id, resume_id, input_data.instruction, holistic_context=None)


def generate_holistic_review_suggestions_for_user(
    user_id: str,
    resume_id: str,
    input_data: GenerateHolisticReviewSuggestionsInput,
) -> PatchSetListDto:
    holistic_context = get_holistic_review_context_for_user(user_id, resume_id)
    context_parts = [
        f"latest compile status: {holistic_context.latestCompileStatus or 'missing'}",
        f"pdf available: {'yes' if holistic_context.pdfUrl else 'no'}",
        f"pdf page count: {holistic_context.pdfPageCount or 'unknown'}",
        f"pdf size kb: {holistic_context.pdfSizeKb or 'unknown'}",
        f"source lines: {holistic_context.sourceLineCount}",
        f"editable blocks: {holistic_context.editableBlockCount}",
    ]
    if holistic_context.editableBlockLabels:
        context_parts.append(f"focus areas: {', '.join(holistic_context.editableBlockLabels)}")
    if holistic_context.layoutSignals:
        context_parts.append(f"layout signals: {', '.join(holistic_context.layoutSignals)}")
    return _generate_review_suggestions_for_user(
        user_id,
        resume_id,
        input_data.instruction,
        holistic_context="; ".join(context_parts),
    )


def _generate_review_suggestions_for_user(
    user_id: str,
    resume_id: str,
    instruction: str,
    holistic_context: str | None,
) -> PatchSetListDto:
    document_model = get_document_model_for_user(user_id, resume_id)
    provider = get_edit_suggestion_provider()
    selected_blocks = document_model.editableBlocks[:3]
    constraint_rules = get_constraint_rules_for_user(user_id, resume_id)

    block_style_examples = {
        block.id: get_relevant_style_examples_for_user(
            user_id,
            resume_id,
            instruction=instruction,
            target_text=block.text,
            preferred_kind=block.kind,
            exclude_texts={block.text},
        )
        for block in selected_blocks
    }

    generated = provider.generate_review_rewrites(
        ReviewSuggestionPrompt(
            instruction=instruction,
            holistic_context=holistic_context,
            blocks=[
                EditSuggestionPrompt(
                    block_kind=block.kind,
                    block_label=block.label,
                    instruction=instruction,
                    text=block.text,
                    style_examples=block_style_examples[block.id],
                    constraints=constraint_rules,
                )
                for block in selected_blocks
            ],
        )
    )

    suggestion_sets: list[PatchSetDto] = []
    for index, block in enumerate(selected_blocks, start=1):
        candidates = generated.get(block.text, [])
        proposals: list[PatchHunkDto] = []

        for candidate_index, after_text in enumerate(candidates[:2], start=1):
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
                    id=f"review-edit-{index}-{candidate_index}",
                    operation="replace",
                    status="validated",
                    targetBlockId=block.id,
                    label=block.label,
                    startLine=block.startLine,
                    endLine=block.endLine,
                    beforeText=block.text,
                    afterText=after_text,
                    rationale=f'Review suggestion from instruction: "{instruction}"',
                    validation=validation,
                )
            )

        if proposals:
            suggestion_sets.append(
                PatchSetDto(
                    id=f"review-set-{block.id}",
                    mode="review",
                    title=f"{'Holistic ' if holistic_context else ''}Review suggestions for {block.label}",
                    summary=instruction,
                    styleExamples=block_style_examples[block.id],
                    retrySeed=0,
                    items=proposals,
                )
            )

    return PatchSetListDto(items=suggestion_sets)


def generate_tailor_suggestions_for_user(
    user_id: str,
    resume_id: str,
    input_data: GenerateTailorSuggestionsInput,
) -> PatchSetListDto:
    create_automatic_snapshot_for_user(
        user_id,
        resume_id,
        _build_tailor_snapshot_name(input_data.jobDescription),
    )
    document_model = get_document_model_for_user(user_id, resume_id)
    provider = get_edit_suggestion_provider()
    selected_blocks = document_model.editableBlocks[:3]
    theme_groups = _extract_tailor_theme_groups(input_data.jobDescription)
    constraint_rules = get_constraint_rules_for_user(user_id, resume_id)

    block_style_examples = {
        block.id: get_relevant_style_examples_for_user(
            user_id,
            resume_id,
            instruction=input_data.instruction,
            target_text=block.text,
            preferred_kind=block.kind,
            exclude_texts={block.text},
        )
        for block in selected_blocks
    }

    generated = provider.generate_tailor_rewrites(
        TailorSuggestionPrompt(
            instruction=input_data.instruction,
            job_description=input_data.jobDescription,
            blocks=[
                EditSuggestionPrompt(
                    block_kind=block.kind,
                    block_label=block.label,
                    instruction=input_data.instruction,
                    text=block.text,
                    style_examples=block_style_examples[block.id],
                    constraints=constraint_rules,
                )
                for block in selected_blocks
            ],
        )
    )

    grouped_suggestion_items: dict[str, list[PatchHunkDto]] = {group["id"]: [] for group in theme_groups}
    assigned_theme_ids: set[str] = set()
    for index, block in enumerate(selected_blocks, start=1):
        candidates = generated.get(block.text, [])
        theme_id = _select_tailor_theme_for_block(block.label, block.text, theme_groups, index - 1, assigned_theme_ids)
        assigned_theme_ids.add(theme_id)

        for candidate_index, after_text in enumerate(candidates[:2], start=1):
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

            grouped_suggestion_items[theme_id].append(
                PatchHunkDto(
                    id=f"tailor-edit-{index}-{candidate_index}",
                    operation="replace",
                    status="validated",
                    targetBlockId=block.id,
                    label=block.label,
                    startLine=block.startLine,
                    endLine=block.endLine,
                    beforeText=block.text,
                    afterText=after_text,
                    rationale=f'Tailor suggestion from instruction: "{input_data.instruction}"',
                    validation=validation,
                )
            )

    suggestion_sets: list[PatchSetDto] = []
    for theme in theme_groups:
        proposals = grouped_suggestion_items[theme["id"]]
        if proposals:
            style_examples = _collect_style_examples_for_theme(proposals, block_style_examples)
            suggestion_sets.append(
                PatchSetDto(
                    id=f"tailor-set-{theme['id']}",
                    mode="tailor",
                    title=theme["title"],
                    summary=theme["summary"],
                    styleExamples=style_examples,
                    retrySeed=0,
                    items=proposals,
                )
            )

    return PatchSetListDto(items=suggestion_sets)


def _build_tailor_snapshot_name(job_description: str) -> str:
    lines = [line.strip() for line in job_description.splitlines() if line.strip()]
    headline = lines[0] if lines else "Untitled role"
    return f"Before tailoring: {headline[:60]}"


def _extract_tailor_theme_groups(job_description: str) -> list[dict[str, str]]:
    lowered = job_description.lower()
    themes: list[dict[str, str]] = []

    if any(term in lowered for term in ["api", "backend", "python", "typescript", "service"]):
        themes.append(
            {
                "id": "backend-api",
                "title": "Backend / API alignment",
                "summary": "Suggestions that better match backend implementation, API, and language expectations from the job description.",
            }
        )

    if any(term in lowered for term in ["distributed", "infrastructure", "platform", "reliability", "scale"]):
        themes.append(
            {
                "id": "systems-infra",
                "title": "Systems / infrastructure alignment",
                "summary": "Suggestions that emphasize systems thinking, infrastructure depth, and operational scale.",
            }
        )

    if any(term in lowered for term in ["lead", "ownership", "stakeholder", "product", "cross-functional"]):
        themes.append(
            {
                "id": "ownership-collaboration",
                "title": "Ownership / collaboration alignment",
                "summary": "Suggestions that highlight ownership, cross-functional collaboration, and product judgment.",
            }
        )

    if not themes:
        themes.append(
            {
                "id": "general-role-fit",
                "title": "General role alignment",
                "summary": "Suggestions that improve overall alignment with the target job description.",
            }
        )

    return themes


def _select_tailor_theme_for_block(
    block_label: str,
    block_text: str,
    theme_groups: list[dict[str, str]],
    fallback_index: int,
    assigned_theme_ids: set[str],
) -> str:
    lowered = f"{block_label} {block_text}".lower()
    preferred_theme_id: str | None = None

    for theme in theme_groups:
        if theme["id"] == "backend-api" and any(term in lowered for term in ["api", "backend", "service", "python", "typescript"]):
            preferred_theme_id = theme["id"]
            break
        if theme["id"] == "systems-infra" and any(term in lowered for term in ["infra", "system", "reliability", "scale", "platform"]):
            preferred_theme_id = theme["id"]
            break
        if theme["id"] == "ownership-collaboration" and any(term in lowered for term in ["lead", "mentor", "product", "team", "stakeholder"]):
            preferred_theme_id = theme["id"]
            break

    if preferred_theme_id and preferred_theme_id not in assigned_theme_ids:
        return preferred_theme_id

    for theme in theme_groups:
        if theme["id"] not in assigned_theme_ids:
            return theme["id"]

    if preferred_theme_id:
        return preferred_theme_id

    return theme_groups[fallback_index % len(theme_groups)]["id"]


def _collect_style_examples_for_theme(
    proposals: list[PatchHunkDto],
    block_style_examples: dict[str, list[str]],
) -> list[str]:
    collected: list[str] = []
    for proposal in proposals:
        for example in block_style_examples.get(proposal.targetBlockId, []):
            if example not in collected:
                collected.append(example)
            if len(collected) >= 3:
                return collected

    return collected
