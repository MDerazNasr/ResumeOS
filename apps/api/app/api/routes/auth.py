from fastapi import APIRouter, Depends, Query, Request, Response

from app.models.schemas import GoogleAuthStatusDto, UpdateUserSettingsInput, UserDto, UserSettingsDto
from app.services.auth import begin_google_auth, complete_google_auth, get_current_user, get_google_auth_status, logout_user
from app.services.settings import get_user_settings, update_user_settings


router = APIRouter()


@router.get("/me", response_model=UserDto)
def read_current_user(current_user: UserDto = Depends(get_current_user)) -> UserDto:
    return current_user


@router.get("/auth/google/status", response_model=GoogleAuthStatusDto)
def google_status() -> GoogleAuthStatusDto:
    return get_google_auth_status()


@router.get("/auth/google/start")
def google_start():
    return begin_google_auth()


@router.get("/auth/google/callback")
def google_callback(
    request: Request,
    code: str = Query(min_length=1),
    state: str | None = None,
):
    return complete_google_auth(code, state, request)


@router.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response) -> None:
    logout_user(request, response)


@router.get("/settings", response_model=UserSettingsDto)
def read_settings(current_user: UserDto = Depends(get_current_user)) -> UserSettingsDto:
    return get_user_settings(current_user.id)


@router.patch("/settings", response_model=UserSettingsDto)
def patch_settings(
    input_data: UpdateUserSettingsInput,
    current_user: UserDto = Depends(get_current_user),
) -> UserSettingsDto:
    return update_user_settings(current_user.id, input_data)
