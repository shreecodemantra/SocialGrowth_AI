from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    TokenError,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate
from app.services.exceptions import AlreadyExistsError, InvalidCredentialsError, NotFoundError


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise AlreadyExistsError("An account with this email already exists.")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        await self.users.add(user)
        await self.session.commit()
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password.")
        if not user.is_active:
            raise InvalidCredentialsError("This account has been deactivated.")
        return user

    def issue_tokens(self, user: User) -> Token:
        subject = str(user.id)
        return Token(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
        )

    async def refresh(self, refresh_token: str) -> Token:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
        except TokenError as exc:
            raise InvalidCredentialsError(str(exc)) from exc

        import uuid

        user = await self.users.get_by_id(uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise NotFoundError("User no longer exists or is inactive.")

        return self.issue_tokens(user)
