import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from jwt import InvalidTokenError

from app.core.config import get_settings


password_hasher = PasswordHasher()


class TokenValidationError(ValueError):
    """Raised when a signed token cannot be used for the requested purpose."""


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerificationError, VerifyMismatchError):
        return False


def _encode_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {**payload, "iat": now, "exp": now + expires_delta},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    return _encode_token(
        {"sub": user_id, "typ": "access"},
        timedelta(minutes=settings.access_token_minutes),
    )


def create_refresh_token(user_id: str, session_id: str) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    token = _encode_token(
        {"sub": user_id, "sid": session_id, "typ": "refresh"},
        timedelta(days=settings.refresh_token_days),
    )
    return token, expires_at


def create_binding_token(openid: str) -> str:
    return _encode_token({"openid": openid, "typ": "bind"}, timedelta(minutes=5))


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError as error:
        raise TokenValidationError("Token is invalid or expired") from error

    if payload.get("typ") != expected_type:
        raise TokenValidationError("Token has an invalid purpose")
    return payload


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_session_id() -> str:
    return secrets.token_urlsafe(24)
