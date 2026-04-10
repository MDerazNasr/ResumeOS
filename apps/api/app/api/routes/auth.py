from fastapi import APIRouter, Depends, Request, Response

from app.models.schemas import LoginInput, RegisterInput, UpdateUserSettingsInput, UserDto, UserSettingsDto
from app.services.auth import get_current_user, login_user, logout_user, register_user
from app.services.settings import get_user_settings, update_user_settings


router = APIRouter()


@router.get("/me", response_model=UserDto)
def read_current_user(current_user: UserDto = Depends(get_current_user)) -> UserDto:
    return current_user


@router.post("/auth/register", response_model=UserDto)
def register(input_data: RegisterInput, response: Response) -> UserDto:
    return register_user(input_data, response)


@router.post("/auth/login", response_model=UserDto)
def login(input_data: LoginInput, response: Response) -> UserDto:
    return login_user(input_data, response)


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
