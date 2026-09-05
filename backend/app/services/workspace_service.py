import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember, WorkspaceRole
from app.repositories.workspace_repository import WorkspaceMemberRepository, WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate
from app.services.exceptions import AlreadyExistsError, NotFoundError, PermissionDeniedError


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug or "workspace"


class WorkspaceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.workspaces = WorkspaceRepository(session)
        self.members = WorkspaceMemberRepository(session)

    async def create_workspace(self, owner: User, data: WorkspaceCreate) -> Workspace:
        base_slug = slugify(data.name)
        slug = base_slug
        suffix = 1
        while await self.workspaces.get_by_slug(slug):
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        workspace = Workspace(name=data.name, slug=slug, owner_id=owner.id)
        await self.workspaces.add(workspace)

        membership = WorkspaceMember(
            workspace_id=workspace.id, user_id=owner.id, role=WorkspaceRole.OWNER
        )
        await self.members.add(membership)

        await self.session.commit()
        return workspace

    async def list_workspaces_for_user(self, user_id: uuid.UUID) -> list[Workspace]:
        return await self.workspaces.list_for_user(user_id)

    async def get_workspace_or_raise(self, workspace_id: uuid.UUID) -> Workspace:
        workspace = await self.workspaces.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found.")
        return workspace

    async def require_role(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, allowed_roles: set[WorkspaceRole]
    ) -> WorkspaceMember:
        membership = await self.members.get_membership(workspace_id, user_id)
        if not membership or membership.role not in allowed_roles:
            raise PermissionDeniedError("You do not have permission to perform this action.")
        return membership

    async def add_member(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, role: WorkspaceRole
    ) -> WorkspaceMember:
        existing = await self.members.get_membership(workspace_id, user_id)
        if existing:
            raise AlreadyExistsError("User is already a member of this workspace.")

        membership = WorkspaceMember(workspace_id=workspace_id, user_id=user_id, role=role)
        await self.members.add(membership)
        await self.session.commit()
        return membership
