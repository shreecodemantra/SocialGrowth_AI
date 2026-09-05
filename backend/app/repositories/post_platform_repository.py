import uuid

from sqlalchemy import select

from app.models.post_platform import PostPlatform
from app.repositories.base import BaseRepository


class PostPlatformRepository(BaseRepository[PostPlatform]):
    model = PostPlatform

    async def get_for_post(self, post_id: uuid.UUID, platform) -> PostPlatform | None:
        result = await self.session.execute(
            select(PostPlatform).where(PostPlatform.post_id == post_id, PostPlatform.platform == platform)
        )
        return result.scalar_one_or_none()
