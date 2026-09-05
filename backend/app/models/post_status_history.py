import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PostStatus
from app.models.mixins import UUIDPrimaryKeyMixin


class PostStatusHistory(UUIDPrimaryKeyMixin, Base):
    """Append-only audit trail (spec section 11) — never update a row, only insert."""

    __tablename__ = "post_status_history"

    post_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[PostStatus] = mapped_column(
        SAEnum(PostStatus, name="post_status_history_status"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post: Mapped["Post"] = relationship(back_populates="status_history")
