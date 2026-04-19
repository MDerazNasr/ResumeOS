from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    ApplyPatchInput,
    ChatResponseDto,
    ChatThreadDto,
    CompileRequestInput,
    CreateChatMessageInput,
    CompileResultDto,
    CreateSnapshotInput,
    CreateResumeInput,
    DocumentModelDto,
    GenerateEditSuggestionsInput,
    GenerateHolisticReviewSuggestionsInput,
    GenerateReviewSuggestionsInput,
    GenerateTailorSuggestionsInput,
    HolisticReviewContextDto,
    LogFeedbackInput,
    PatchValidationResultDto,
    PatchSetListDto,
    ResumeConstraintsDto,
    RestoreSnapshotInput,
    ResumeDto,
    ResumeListResponseDto,
    SnapshotDto,
    SnapshotDetailDto,
    SnapshotListResponseDto,
    UpdateDraftInput,
    UpdateResumeConstraintsInput,
    UserDto,
    ValidatePatchInput,
    WorkingDraftDto,
)
from app.services.compile import compile_resume_source_for_user
from app.services.compile import get_latest_pdf_for_user
from app.services.auth import get_current_user
from app.services.chat import create_chat_message_for_user, get_chat_thread_for_user, stream_chat_message_for_user
from app.services.constraints import get_resume_constraints_for_user, update_resume_constraints_for_user
from app.services.document_model import get_document_model_for_user
from app.services.edit_suggestions import (
    generate_edit_suggestions_for_user,
    generate_holistic_review_suggestions_for_user,
    generate_review_suggestions_for_user,
    generate_tailor_suggestions_for_user,
)
from app.services.feedback import log_feedback_for_user
from app.services.holistic_review import get_holistic_review_context_for_user
from app.services.mock_patches import list_seeded_patch_sets_for_user
from app.services.patch_apply import apply_patch_for_user
from app.services.patch_validation import validate_patch_for_user
from app.services.resumes import (
    create_resume_for_user,
    get_draft_for_user,
    get_resume_for_user,
    list_resumes_for_user,
    save_draft_for_user,
)
from app.services.snapshots import (
    create_snapshot_for_user,
    get_snapshot_for_user,
    list_snapshots_for_user,
    restore_snapshot_for_user,
)


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("", response_model=ResumeListResponseDto)
def list_resumes(current_user: UserDto = Depends(get_current_user)) -> ResumeListResponseDto:
    return list_resumes_for_user(current_user.id)


@router.post("", response_model=ResumeDto)
def create_resume(
    input_data: CreateResumeInput,
    current_user: UserDto = Depends(get_current_user),
) -> ResumeDto:
    return create_resume_for_user(current_user.id, input_data)


@router.get("/{resume_id}", response_model=ResumeDto)
def get_resume(resume_id: str, current_user: UserDto = Depends(get_current_user)) -> ResumeDto:
    return get_resume_for_user(current_user.id, resume_id)


@router.get("/{resume_id}/draft", response_model=WorkingDraftDto)
def get_draft(resume_id: str, current_user: UserDto = Depends(get_current_user)) -> WorkingDraftDto:
    return get_draft_for_user(current_user.id, resume_id)


@router.get("/{resume_id}/document-model", response_model=DocumentModelDto)
def get_document_model(resume_id: str, current_user: UserDto = Depends(get_current_user)) -> DocumentModelDto:
    return get_document_model_for_user(current_user.id, resume_id)


@router.get("/{resume_id}/constraints", response_model=ResumeConstraintsDto)
def get_resume_constraints(
    resume_id: str,
    current_user: UserDto = Depends(get_current_user),
) -> ResumeConstraintsDto:
    return get_resume_constraints_for_user(current_user.id, resume_id)


@router.patch("/{resume_id}/constraints", response_model=ResumeConstraintsDto)
def update_resume_constraints(
    resume_id: str,
    input_data: UpdateResumeConstraintsInput,
    current_user: UserDto = Depends(get_current_user),
) -> ResumeConstraintsDto:
    return update_resume_constraints_for_user(current_user.id, resume_id, input_data)


@router.get("/{resume_id}/holistic-review/context", response_model=HolisticReviewContextDto)
def get_holistic_review_context(
    resume_id: str,
    current_user: UserDto = Depends(get_current_user),
) -> HolisticReviewContextDto:
    return get_holistic_review_context_for_user(current_user.id, resume_id)


@router.post("/{resume_id}/patches/validate", response_model=PatchValidationResultDto)
def validate_patch(
    resume_id: str,
    input_data: ValidatePatchInput,
    current_user: UserDto = Depends(get_current_user),
) -> PatchValidationResultDto:
    return validate_patch_for_user(current_user.id, resume_id, input_data)


@router.get("/{resume_id}/patch-sets/seeded", response_model=PatchSetListDto)
def list_seeded_patch_sets(
    resume_id: str,
    seed: int = 0,
    current_user: UserDto = Depends(get_current_user),
) -> PatchSetListDto:
    return list_seeded_patch_sets_for_user(current_user.id, resume_id, seed)


@router.post("/{resume_id}/suggestions/edit", response_model=PatchSetListDto)
def generate_edit_suggestions(
    resume_id: str,
    input_data: GenerateEditSuggestionsInput,
    current_user: UserDto = Depends(get_current_user),
) -> PatchSetListDto:
    return generate_edit_suggestions_for_user(current_user.id, resume_id, input_data)


@router.post("/{resume_id}/suggestions/review", response_model=PatchSetListDto)
def generate_review_suggestions(
    resume_id: str,
    input_data: GenerateReviewSuggestionsInput,
    current_user: UserDto = Depends(get_current_user),
) -> PatchSetListDto:
    return generate_review_suggestions_for_user(current_user.id, resume_id, input_data)


@router.post("/{resume_id}/suggestions/holistic-review", response_model=PatchSetListDto)
def generate_holistic_review_suggestions(
    resume_id: str,
    input_data: GenerateHolisticReviewSuggestionsInput,
    current_user: UserDto = Depends(get_current_user),
) -> PatchSetListDto:
    return generate_holistic_review_suggestions_for_user(current_user.id, resume_id, input_data)


@router.post("/{resume_id}/suggestions/tailor", response_model=PatchSetListDto)
def generate_tailor_suggestions(
    resume_id: str,
    input_data: GenerateTailorSuggestionsInput,
    current_user: UserDto = Depends(get_current_user),
) -> PatchSetListDto:
    return generate_tailor_suggestions_for_user(current_user.id, resume_id, input_data)


@router.post("/{resume_id}/patches/apply", response_model=WorkingDraftDto)
def apply_patch(
    resume_id: str,
    input_data: ApplyPatchInput,
    current_user: UserDto = Depends(get_current_user),
) -> WorkingDraftDto:
    return apply_patch_for_user(current_user.id, resume_id, input_data)


@router.get("/{resume_id}/chat", response_model=ChatThreadDto)
def get_chat_thread(
    resume_id: str,
    current_user: UserDto = Depends(get_current_user),
) -> ChatThreadDto:
    return get_chat_thread_for_user(current_user.id, resume_id)


@router.post("/{resume_id}/chat/messages", response_model=ChatResponseDto)
def create_chat_message(
    resume_id: str,
    input_data: CreateChatMessageInput,
    current_user: UserDto = Depends(get_current_user),
) -> ChatResponseDto:
    return create_chat_message_for_user(current_user.id, resume_id, input_data)


@router.post("/{resume_id}/chat/messages/stream")
async def stream_chat_message(
    resume_id: str,
    input_data: CreateChatMessageInput,
    current_user: UserDto = Depends(get_current_user),
):
    return StreamingResponse(
        stream_chat_message_for_user(current_user.id, resume_id, input_data),
        media_type="application/x-ndjson",
    )


@router.post("/{resume_id}/feedback", status_code=204)
def log_feedback(
    resume_id: str,
    input_data: LogFeedbackInput,
    current_user: UserDto = Depends(get_current_user),
) -> None:
    log_feedback_for_user(current_user.id, resume_id, input_data)


@router.put("/{resume_id}/draft", response_model=WorkingDraftDto)
def update_draft(
    resume_id: str,
    input_data: UpdateDraftInput,
    current_user: UserDto = Depends(get_current_user),
) -> WorkingDraftDto:
    return save_draft_for_user(current_user.id, resume_id, input_data.sourceTex, input_data.version)


@router.post("/{resume_id}/compile", response_model=CompileResultDto)
def compile_resume(
    resume_id: str,
    input_data: CompileRequestInput,
    current_user: UserDto = Depends(get_current_user),
) -> CompileResultDto:
    return compile_resume_source_for_user(
        current_user.id,
        resume_id,
        input_data.sourceTex,
        input_data.draftVersion,
    )


@router.get("/{resume_id}/compile/latest.pdf")
def get_latest_pdf(resume_id: str, current_user: UserDto = Depends(get_current_user)):
    return get_latest_pdf_for_user(current_user.id, resume_id)


@router.get("/{resume_id}/snapshots", response_model=SnapshotListResponseDto)
def list_snapshots(resume_id: str, current_user: UserDto = Depends(get_current_user)) -> SnapshotListResponseDto:
    return list_snapshots_for_user(current_user.id, resume_id)


@router.post("/{resume_id}/snapshots", response_model=SnapshotDto)
def create_snapshot(
    resume_id: str,
    input_data: CreateSnapshotInput,
    current_user: UserDto = Depends(get_current_user),
) -> SnapshotDto:
    return create_snapshot_for_user(current_user.id, resume_id, input_data)


@router.get("/{resume_id}/snapshots/{snapshot_id}", response_model=SnapshotDetailDto)
def get_snapshot(
    resume_id: str,
    snapshot_id: str,
    current_user: UserDto = Depends(get_current_user),
) -> SnapshotDetailDto:
    return get_snapshot_for_user(current_user.id, resume_id, snapshot_id)


@router.post("/{resume_id}/snapshots/restore", response_model=WorkingDraftDto)
def restore_snapshot(
    resume_id: str,
    input_data: RestoreSnapshotInput,
    current_user: UserDto = Depends(get_current_user),
) -> WorkingDraftDto:
    return restore_snapshot_for_user(current_user.id, resume_id, input_data.snapshotId)
