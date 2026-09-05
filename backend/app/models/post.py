import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PostStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Post(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    The overall post (spec section 10) — one per campaign per conceptual
    piece of content. Each selected platform gets its own `PostPlatform`
    child row with independent content/status/external ID, since platforms
    publish and get approved independently of one another.
    """

    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("workspace_id", "display_id", name="uq_posts_workspace_display_id"),)

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False
    )

    # Human-friendly id, e.g. "POST-2026-000001" — see PostRepository.next_display_id.
    display_id: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    status: Mapped[PostStatus] = mapped_column(
        SAEnum(PostStatus, name="post_status"), nullable=False, default=PostStatus.DRAFT
    )
    content_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # filled in Phase 6

    campaign: Mapped["Campaign"] = relationship(back_populates="posts")
    platforms: Mapped[list["PostPlatform"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    status_history: Mapped[list["PostStatusHistory"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", order_by="PostStatusHistory.created_at"
    )
