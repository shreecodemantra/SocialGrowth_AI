import uuid

from sqlalchemy import select

from app.models.brand_profile import BrandProfile
from app.repositories.base import BaseRepository


class BrandProfileRepository(BaseRepository[BrandProfile]):
    model = BrandProfile

    async def get_by_workspace(self, workspace_id: uuid.UUID) -> BrandProfile | None:
        result = await self.session.execute(
            select(BrandProfile).where(BrandProfile.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()
