from fastapi import APIRouter, Depends

from app.models.schemas import (
    CreateResumeInput,
    ResumeDto,
    ResumeListResponseDto,
    UpdateDraftInput,
    UserDto,
    WorkingDraftDto,
)
from app.services.auth import get_current_user
from app.services.resumes import (
    create_resume_for_user,
    get_draft_for_user,
    get_resume_for_user,
    list_resumes_for_user,
    save_draft_for_user,
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


@router.put("/{resume_id}/draft", response_model=WorkingDraftDto)
def update_draft(
    resume_id: str,
    input_data: UpdateDraftInput,
    current_user: UserDto = Depends(get_current_user),
) -> WorkingDraftDto:
    return save_draft_for_user(current_user.id, resume_id, input_data.sourceTex, input_data.version)

