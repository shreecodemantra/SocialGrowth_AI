import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_any_member
from app.db.session import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceMemberInvite, WorkspaceMemberOut, WorkspaceOut
from app.services.exceptions import DomainError
from app.services.workspace_service import WorkspaceService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def _raise_domain_error(exc: DomainError):
    raise HTTPException(
        status_code=exc.status_code,
        detail={"success": False, "error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable}},
    )


@router.post("", response_model=WorkspaceOut, status_code=201)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkspaceService(db)
    return await service.create_workspace(current_user, data)


@router.get("", response_model=list[WorkspaceOut])
async def list_my_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkspaceService(db)
    return await service.list_workspaces_for_user(current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(
    workspace_id: uuid.UUID,
    _membership: WorkspaceMember = Depends(require_any_member),
    db: AsyncSession = Depends(get_db),
):
    service = WorkspaceService(db)
    try:
        return await service.get_workspace_or_raise(workspace_id)
    except DomainError as exc:
        _raise_domain_error(exc)


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberOut, status_code=201)
async def invite_member(
    workspace_id: uuid.UUID,
    data: WorkspaceMemberInvite,
    _membership: WorkspaceMember = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    target_user = await UserRepository(db).get_by_email(data.email)
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": {"code": "USER_NOT_FOUND", "message": "No user with this email exists yet.", "retryable": False}},
        )

    service = WorkspaceService(db)
    try:
        return await service.add_member(workspace_id, target_user.id, data.role)
    except DomainError as exc:
        _raise_domain_error(exc)
