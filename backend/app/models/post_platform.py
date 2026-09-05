import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum as SAEnum, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PlatformType, PostStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PostPlatform(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One platform's rendering of a Post. `content` holds the structured,
    platform-specific fields from spec section 5 (different shape per
    platform — see app/schemas/content.py for what each platform expects).
    """

    __tablename__ = "post_platforms"
    __table_args__ = (UniqueConstraint("post_id", "platform", name="uq_post_platforms_post_platform"),)

    post_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[PlatformType] = mapped_column(SAEnum(PlatformType, name="platform_type"), nullable=False)

    content: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        SAEnum(PostStatus, name="post_platform_status"), nullable=False, default=PostStatus.DRAFT
    )
    # Flagged by the quality agent (forbidden-word checks) at generation/edit
    # time — surfaced to the reviewer, never silently blocks generation.
    quality_violations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    primary_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )

    external_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Phase 3
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # Phase 3/4

    post: Mapped["Post"] = relationship(back_populates="platforms")
    primary_asset: Mapped["Asset | None"] = relationship(foreign_keys=[primary_asset_id])
