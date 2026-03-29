from app.models.schemas import UserDto


DEV_USER = UserDto(
    id="usr_dev_resumeos",
    email="dev@resumeos.local",
    name="ResumeOS Dev",
)


def get_current_user() -> UserDto:
    return DEV_USER

