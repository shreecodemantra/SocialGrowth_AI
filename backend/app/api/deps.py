"""
Shared FastAPI dependencies: DB session, current user, and workspace-role
enforcement (see section 29 — OWNER/ADMIN/EDITOR/VIEWER).
"""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenError, decode_token
from app.db.session import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceMemberRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"success": False, "error": {"code": "INVALID_TOKEN", "message": "Could not validate credentials.", "retryable": False}},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token, expected_type="access")
    except TokenError as exc:
        raise _credentials_exception() from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise _credentials_exception() from exc

    user = await UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise _credentials_exception()

    return user


async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser privileges required.")
    return current_user


class WorkspaceRoleChecker:
    """
    Dependency factory: `Depends(WorkspaceRoleChecker({WorkspaceRole.OWNER, WorkspaceRole.ADMIN}))`
    resolves the caller's membership for the `workspace_id` path parameter and
    enforces it is one of `allowed_roles`.
    """

    def __init__(self, allowed_roles: set[WorkspaceRole]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        workspace_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> WorkspaceMember:
        membership = await WorkspaceMemberRepository(db).get_membership(workspace_id, current_user.id)
        if not membership or membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "error": {
                        "code": "PERMISSION_DENIED",
                        "message": "You do not have permission to perform this action in this workspace.",
                        "retryable": False,
                    },
                },
            )
        return membership


require_any_member = WorkspaceRoleChecker(
    {WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.EDITOR, WorkspaceRole.VIEWER}
)
require_editor = WorkspaceRoleChecker(
    {WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.EDITOR}
)
require_admin = WorkspaceRoleChecker({WorkspaceRole.OWNER, WorkspaceRole.ADMIN})
require_owner = WorkspaceRoleChecker({WorkspaceRole.OWNER})
