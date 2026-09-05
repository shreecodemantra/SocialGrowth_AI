import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.campaign import Campaign
from app.models.post import Post
from app.models.post_platform import PostPlatform
from app.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    model = Campaign

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Campaign]:
        result = await self.session.execute(
            select(Campaign).where(Campaign.workspace_id == workspace_id).order_by(Campaign.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_posts(self, campaign_id: uuid.UUID) -> Campaign | None:
        result = await self.session.execute(
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(
                selectinload(Campaign.posts).selectinload(Post.platforms).selectinload(PostPlatform.primary_asset),
                selectinload(Campaign.posts).selectinload(Post.status_history),
            )
        )
        return result.scalar_one_or_none()
