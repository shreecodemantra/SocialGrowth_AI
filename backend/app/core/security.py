"""
Password hashing and JWT access/refresh token issuance & verification.

Security notes:
- Passwords are hashed with bcrypt via passlib; plaintext is never stored or logged.
- Access tokens are short-lived; refresh tokens are longer-lived and carry a
  distinct `type` claim so one cannot be used in place of the other.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(subject, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, "refresh", timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))


class TokenError(Exception):
    pass


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token")

    return payload
