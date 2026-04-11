from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import uuid
from urllib.parse import urlencode
from datetime import UTC, datetime, timedelta
from time import time

import httpx
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.db.database import get_connection
from app.models.schemas import GoogleAuthStatusDto, UserDto
from app.services.utils import utc_now_iso


SESSION_COOKIE_NAME = "resumeos_session"
GOOGLE_STATE_COOKIE_NAME = "resumeos_google_state"
SESSION_DURATION_DAYS = 14
GOOGLE_AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_STATE_MAX_AGE_SECONDS = 600


def ensure_auth_schema() -> None:
    with get_connection() as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        if "google_sub" not in columns:
            connection.execute("ALTER TABLE users ADD COLUMN google_sub TEXT")

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
            CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub_unique
            ON users(google_sub)
            WHERE google_sub IS NOT NULL
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
              user_id TEXT PRIMARY KEY,
              editor_mode TEXT NOT NULL DEFAULT 'standard',
              theme_mode TEXT NOT NULL DEFAULT 'dark',
              updated_at TEXT NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        settings_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(user_settings)").fetchall()
        }
        if "theme_mode" not in settings_columns:
            connection.execute("ALTER TABLE user_settings ADD COLUMN theme_mode TEXT NOT NULL DEFAULT 'dark'")
        connection.commit()


def get_google_auth_status() -> GoogleAuthStatusDto:
    return GoogleAuthStatusDto(configured=is_google_auth_configured())


def is_google_auth_configured() -> bool:
    return bool(
        os.getenv("RESUMEOS_GOOGLE_CLIENT_ID")
        and os.getenv("RESUMEOS_GOOGLE_CLIENT_SECRET")
        and os.getenv("RESUMEOS_GOOGLE_REDIRECT_URI")
    )


def begin_google_auth() -> RedirectResponse:
    ensure_auth_schema()
    _require_google_auth_configured()

    state = _create_signed_oauth_state()
    response = RedirectResponse(url=_build_google_auth_url(state), status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.set_cookie(
        GOOGLE_STATE_COOKIE_NAME,
        state,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=GOOGLE_STATE_MAX_AGE_SECONDS,
    )
    return response


def complete_google_auth(code: str, state: str | None, request: Request) -> RedirectResponse:
    ensure_auth_schema()
    _require_google_auth_configured()

    expected_state = request.cookies.get(GOOGLE_STATE_COOKIE_NAME)
    if not state or not _is_valid_signed_oauth_state(state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state.")

    if expected_state is not None and not hmac.compare_digest(state, expected_state):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state.")

    token_data = exchange_google_code(code)
    profile = fetch_google_profile(token_data["access_token"])
    user = _upsert_google_user(profile)

    response = RedirectResponse(url=_web_app_success_url(), status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    response.delete_cookie(GOOGLE_STATE_COOKIE_NAME, path="/")
    _create_session_for_user(user.id, response)
    return response


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

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")


def exchange_google_code(code: str) -> dict[str, str]:
    payload = {
        "code": code,
        "client_id": os.environ["RESUMEOS_GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["RESUMEOS_GOOGLE_CLIENT_SECRET"],
        "redirect_uri": os.environ["RESUMEOS_GOOGLE_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }
    with httpx.Client(timeout=10.0) as client:
        response = client.post(GOOGLE_TOKEN_URL, data=payload)
        response.raise_for_status()
        data = response.json()

    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google token exchange failed.")

    return data


def fetch_google_profile(access_token: str) -> dict[str, str]:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()

    if not data.get("sub") or not data.get("email") or not data.get("name"):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google profile response was incomplete.")

    return data


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

    return UserDto(id=row["id"], email=row["email"], name=row["name"])

def _hash_session_token(session_token: str) -> str:
    secret = os.getenv("RESUMEOS_SESSION_SECRET", "resumeos-dev-session-secret")
    return hashlib.sha256(f"{secret}:{session_token}".encode("utf-8")).hexdigest()


def _build_google_auth_url(state: str) -> str:
    query = urlencode(
        {
            "client_id": os.environ["RESUMEOS_GOOGLE_CLIENT_ID"],
            "redirect_uri": os.environ["RESUMEOS_GOOGLE_REDIRECT_URI"],
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return f"{GOOGLE_AUTH_BASE_URL}?{query}"


def _upsert_google_user(profile: dict[str, str]) -> UserDto:
    ensure_auth_schema()
    timestamp = utc_now_iso()
    google_sub = profile["sub"]
    email = profile["email"].strip()
    name = profile["name"].strip()

    with get_connection() as connection:
        existing_google = connection.execute(
            """
            SELECT id, email, name
            FROM users
            WHERE google_sub = ?
            """,
            (google_sub,),
        ).fetchone()
        if existing_google is not None:
            connection.execute(
                """
                UPDATE users
                SET email = ?, name = ?, updated_at = ?
                WHERE id = ?
                """,
                (email, name, timestamp, existing_google["id"]),
            )
            connection.commit()
            return UserDto(id=existing_google["id"], email=email, name=name)

        existing_email = connection.execute(
            """
            SELECT id, email, name
            FROM users
            WHERE lower(email) = lower(?)
            """,
            (email,),
        ).fetchone()
        if existing_email is not None:
            connection.execute(
                """
                UPDATE users
                SET google_sub = ?, name = ?, updated_at = ?
                WHERE id = ?
                """,
                (google_sub, name, timestamp, existing_email["id"]),
            )
            _ensure_user_settings(connection, existing_email["id"], timestamp)
            connection.commit()
            return UserDto(id=existing_email["id"], email=existing_email["email"], name=name)

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        connection.execute(
            """
            INSERT INTO users (id, email, name, google_sub, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, email, name, google_sub, timestamp, timestamp),
        )
        _ensure_user_settings(connection, user_id, timestamp)
        connection.commit()
        return UserDto(id=user_id, email=email, name=name)


def _ensure_user_settings(connection, user_id: str, timestamp: str) -> None:
    connection.execute(
        """
        INSERT INTO user_settings (user_id, editor_mode, theme_mode, updated_at)
        VALUES (?, 'standard', 'dark', ?)
        ON CONFLICT(user_id) DO NOTHING
        """,
        (user_id, timestamp),
    )


def _require_google_auth_configured() -> None:
    if not is_google_auth_configured():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google auth is not configured.")


def _web_app_success_url() -> str:
    return os.getenv("RESUMEOS_WEB_BASE_URL", "http://127.0.0.1:3000") + "/app/resumes"


def _create_signed_oauth_state() -> str:
    nonce = secrets.token_urlsafe(24)
    issued_at = str(int(time()))
    payload = f"{nonce}.{issued_at}"
    signature = _sign_oauth_state(payload)
    return f"{payload}.{signature}"


def _is_valid_signed_oauth_state(state: str) -> bool:
    try:
        nonce, issued_at_raw, signature = state.split(".", 2)
    except ValueError:
        return False

    if not nonce or not issued_at_raw or not signature:
        return False

    payload = f"{nonce}.{issued_at_raw}"
    expected_signature = _sign_oauth_state(payload)
    if not hmac.compare_digest(signature, expected_signature):
        return False

    try:
        issued_at = int(issued_at_raw)
    except ValueError:
        return False

    if int(time()) - issued_at > GOOGLE_STATE_MAX_AGE_SECONDS:
        return False

    return True


def _sign_oauth_state(payload: str) -> str:
    secret = os.getenv("RESUMEOS_SESSION_SECRET", "resumeos-dev-session-secret")
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
