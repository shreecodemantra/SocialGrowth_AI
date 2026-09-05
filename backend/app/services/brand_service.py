import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand_profile import BrandProfile
from app.repositories.brand_repository import BrandProfileRepository
from app.schemas.brand import BrandProfileUpsert


class BrandService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.brands = BrandProfileRepository(session)

    async def get(self, workspace_id: uuid.UUID) -> BrandProfile | None:
        return await self.brands.get_by_workspace(workspace_id)

    async def upsert(self, workspace_id: uuid.UUID, data: BrandProfileUpsert) -> BrandProfile:
        profile = await self.brands.get_by_workspace(workspace_id)
        fields = data.model_dump()

        if profile is None:
            profile = BrandProfile(workspace_id=workspace_id, **fields)
            await self.brands.add(profile)
        else:
            for key, value in fields.items():
                setattr(profile, key, value)

        await self.session.commit()
        return profile
