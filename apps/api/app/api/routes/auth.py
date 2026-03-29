from fastapi import APIRouter, Depends

from app.models.schemas import UserDto
from app.services.auth import get_current_user


router = APIRouter()


@router.get("/me", response_model=UserDto)
def read_current_user(current_user: UserDto = Depends(get_current_user)) -> UserDto:
    return current_user

