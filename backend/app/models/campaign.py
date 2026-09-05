import uuid

from sqlalchemy import JSON, Enum as SAEnum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CampaignStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Campaign(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    One user-entered topic/idea (spec section 5) fans out into one Post per
    selected platform. `platforms` records what was requested at creation
    time; each resulting Post/PostPlatform row is the durable record.
    """

    __tablename__ = "campaigns"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    goal: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_audience: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    platforms: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    generate_images: Mapped[bool] = mapped_column(default=True, nullable=False)
    generate_video: Mapped[bool] = mapped_column(default=False, nullable=False)

    status: Mapped[CampaignStatus] = mapped_column(
        SAEnum(CampaignStatus, name="campaign_status"), nullable=False, default=CampaignStatus.DRAFT
    )
    failure_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="campaign", cascade="all, delete-orphan")
