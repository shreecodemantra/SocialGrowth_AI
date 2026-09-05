import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.models.post_platform import PostPlatform
from app.models.post_status_history import PostStatusHistory
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    model = Post

    async def next_display_id(self, workspace_id: uuid.UUID) -> str:
        """
        Formats "POST-<year>-<seq>" per spec section 10. Counts existing
        posts for the workspace this calendar year — simple and portable
        across Postgres/SQLite, at the cost of a small race window under
        concurrent creation for the same workspace; harden with a DB
        sequence if/when that becomes a real contention point.
        """
        year = datetime.now(timezone.utc).year
        result = await self.session.execute(
            select(func.count()).select_from(Post).where(Post.workspace_id == workspace_id)
        )
        count = result.scalar_one()
        return f"POST-{year}-{count + 1:06d}"

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Post]:
        result = await self.session.execute(
            select(Post)
            .where(Post.workspace_id == workspace_id)
            .options(
                selectinload(Post.platforms).selectinload(PostPlatform.primary_asset),
                selectinload(Post.status_history),
            )
            .order_by(Post.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_platforms(self, post_id: uuid.UUID) -> Post | None:
        result = await self.session.execute(
            select(Post)
            .where(Post.id == post_id)
            .options(
                selectinload(Post.platforms).selectinload(PostPlatform.primary_asset),
                selectinload(Post.status_history),
            )
        )
        return result.scalar_one_or_none()

    async def add_status_history(self, post_id: uuid.UUID, status, note: str | None = None) -> None:
        self.session.add(PostStatusHistory(post_id=post_id, status=status, note=note))
        await self.session.flush()
