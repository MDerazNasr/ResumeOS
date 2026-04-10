from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.schemas import UpdateUserSettingsInput, UserSettingsDto
from app.services.auth import ensure_auth_schema
from app.services.utils import utc_now_iso


def get_user_settings(user_id: str) -> UserSettingsDto:
    ensure_auth_schema()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT editor_mode
            FROM user_settings
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        if row is None:
            timestamp = utc_now_iso()
            connection.execute(
                """
                INSERT INTO user_settings (user_id, editor_mode, updated_at)
                VALUES (?, 'standard', ?)
                """,
                (user_id, timestamp),
            )
            connection.commit()
            return UserSettingsDto(editorMode="standard")

    return UserSettingsDto(editorMode=row["editor_mode"])


def update_user_settings(user_id: str, input_data: UpdateUserSettingsInput) -> UserSettingsDto:
    ensure_auth_schema()
    current = get_user_settings(user_id)
    next_editor_mode = input_data.editorMode or current.editorMode

    if next_editor_mode not in {"standard", "vim"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported editor mode.")

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE user_settings
            SET editor_mode = ?, updated_at = ?
            WHERE user_id = ?
            """,
            (next_editor_mode, utc_now_iso(), user_id),
        )
        connection.commit()

    return UserSettingsDto(editorMode=next_editor_mode)
