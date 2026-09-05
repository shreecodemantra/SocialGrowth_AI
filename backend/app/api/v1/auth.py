from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import RefreshRequest, Token
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import AuthService
from app.services.exceptions import DomainError

router = APIRouter(prefix="/auth", tags=["auth"])


def _raise_domain_error(exc: DomainError):
    raise HTTPException(
        status_code=exc.status_code,
        detail={"success": False, "error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable}},
    )


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        user = await service.register(data)
    except DomainError as exc:
        _raise_domain_error(exc)
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        user = await service.authenticate(form_data.username, form_data.password)
    except DomainError as exc:
        _raise_domain_error(exc)
    return service.issue_tokens(user)


@router.post("/refresh", response_model=Token)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        return await service.refresh(data.refresh_token)
    except DomainError as exc:
        _raise_domain_error(exc)
