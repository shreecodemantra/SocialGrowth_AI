import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """
    A Workspace is the tenant boundary: it owns a Brand, connected Social
    Accounts, Campaigns/Posts, and Analytics. The first workspace created
    for this deployment represents "Shree Code Mantra".
    """

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="owned_workspaces")
    members: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    brand_profile: Mapped["BrandProfile | None"] = relationship(
        back_populates="workspace", cascade="all, delete-orphan", uselist=False
    )
