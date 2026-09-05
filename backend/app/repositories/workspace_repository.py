import uuid

from sqlalchemy import select

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    model = Workspace

    async def get_by_slug(self, slug: str) -> Workspace | None:
        result = await self.session.execute(select(Workspace).where(Workspace.slug == slug))
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Workspace]:
        result = await self.session.execute(
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
        )
        return list(result.scalars().all())


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    model = WorkspaceMember

    async def get_membership(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> WorkspaceMember | None:
        result = await self.session.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
