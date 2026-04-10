from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request, Response, status

from app.db.database import get_connection
from app.models.schemas import LoginInput, RegisterInput, UserDto
from app.services.utils import utc_now_iso


SESSION_COOKIE_NAME = "resumeos_session"
SESSION_DURATION_DAYS = 14

DEV_USER = UserDto(
    id="usr_dev_resumeos",
    email="dev@resumeos.local",
    name="ResumeOS Dev",
    authSource="dev_fallback",
)


def ensure_auth_schema() -> None:
    with get_connection() as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "password_hash" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              token_hash TEXT NOT NULL UNIQUE,
              created_at TEXT NOT NULL,
              expires_at TEXT NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
              user_id TEXT PRIMARY KEY,
              editor_mode TEXT NOT NULL DEFAULT 'standard',
              updated_at TEXT NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        connection.commit()


def ensure_dev_user_exists() -> None:
    timestamp = utc_now_iso()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, NULL, ?, ?)
            ON CONFLICT(id) DO UPDATE SET email = excluded.email, name = excluded.name, updated_at = excluded.updated_at
            """,
            (DEV_USER.id, DEV_USER.email, DEV_USER.name, timestamp, timestamp),
        )
        connection.execute(
            """
            INSERT INTO user_settings (user_id, editor_mode, updated_at)
            VALUES (?, 'standard', ?)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (DEV_USER.id, timestamp),
        )
        connection.commit()


def register_user(input_data: RegisterInput, response: Response) -> UserDto:
    ensure_auth_schema()
    timestamp = utc_now_iso()
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    password_hash = _hash_password(input_data.password)

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT 1 FROM users WHERE lower(email) = lower(?)",
            (input_data.email.strip(),),
        ).fetchone()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered.")

        connection.execute(
            """
            INSERT INTO users (id, email, name, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                input_data.email.strip(),
                input_data.name.strip(),
                password_hash,
                timestamp,
                timestamp,
            ),
        )
        connection.execute(
            """
            INSERT INTO user_settings (user_id, editor_mode, updated_at)
            VALUES (?, 'standard', ?)
            """,
            (user_id, timestamp),
        )
        connection.commit()

    user = UserDto(id=user_id, email=input_data.email.strip(), name=input_data.name.strip(), authSource="session")
    _create_session_for_user(user_id, response)
    return user


def login_user(input_data: LoginInput, response: Response) -> UserDto:
    ensure_auth_schema()
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, email, name, password_hash
            FROM users
            WHERE lower(email) = lower(?)
            """,
            (input_data.email.strip(),),
        ).fetchone()

    if row is None or row["password_hash"] is None or not _verify_password(input_data.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    _create_session_for_user(row["id"], response)
    return UserDto(id=row["id"], email=row["email"], name=row["name"], authSource="session")


def logout_user(request: Request, response: Response) -> None:
    ensure_auth_schema()
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token:
        session_hash = _hash_session_token(session_token)
        with get_connection() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (session_hash,))
            connection.commit()

    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def get_current_user(request: Request) -> UserDto:
    ensure_auth_schema()
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token:
        user = _get_user_from_session_token(session_token)
        if user is not None:
            return user

    return DEV_USER


def _create_session_for_user(user_id: str, response: Response) -> None:
    token = secrets.token_urlsafe(32)
    session_hash = _hash_session_token(token)
    created_at = datetime.now(UTC)
    expires_at = created_at + timedelta(days=SESSION_DURATION_DAYS)

    with get_connection() as connection:
        connection.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        connection.execute(
            """
            INSERT INTO sessions (id, user_id, token_hash, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                f"sess_{uuid.uuid4().hex[:12]}",
                user_id,
                session_hash,
                created_at.isoformat(),
                expires_at.isoformat(),
            ),
        )
        connection.commit()

    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=int(timedelta(days=SESSION_DURATION_DAYS).total_seconds()),
    )


def _get_user_from_session_token(session_token: str) -> UserDto | None:
    session_hash = _hash_session_token(session_token)
    now = datetime.now(UTC).isoformat()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT u.id, u.email, u.name
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ? AND s.expires_at > ?
            """,
            (session_hash, now),
        ).fetchone()

    if row is None:
        return None

    return UserDto(id=row["id"], email=row["email"], name=row["name"], authSource="session")


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()
    return f"{salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split("$", 1)
    except ValueError:
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000).hex()
    return hmac.compare_digest(candidate, digest)


def _hash_session_token(session_token: str) -> str:
    secret = os.getenv("RESUMEOS_SESSION_SECRET", "resumeos-dev-session-secret")
    return hashlib.sha256(f"{secret}:{session_token}".encode("utf-8")).hexdigest()
