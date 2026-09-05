import uuid

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BrandProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """
    One brand profile per workspace. The AI content pipeline (Phase 2+)
    reads this whenever it generates or scores content.
    """

    __tablename__ = "brand_profiles"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    brand_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True)

    target_audience: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    target_countries: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    target_languages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    brand_tone: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    forbidden_words: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    cta_style: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_hashtags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    brand_colors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    workspace: Mapped["Workspace"] = relationship(back_populates="brand_profile")
