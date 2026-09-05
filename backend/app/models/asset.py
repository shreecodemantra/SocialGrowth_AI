import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AssetType
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Generated media (image/video/thumbnail), stored in object storage —
    only the resulting URL lives here (spec section 7)."""

    __tablename__ = "assets"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True
    )
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=True
    )
    post_platform_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("post_platforms.id", ondelete="CASCADE"), nullable=True
    )

    asset_type: Mapped[AssetType] = mapped_column(SAEnum(AssetType, name="asset_type"), nullable=False)
    storage_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, default="image/png")
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generation_prompt: Mapped[str | None] = mapped_column(String(4000), nullable=True)
