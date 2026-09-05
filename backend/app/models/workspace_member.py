import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class WorkspaceRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


class WorkspaceMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member_workspace_user"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        SAEnum(WorkspaceRole, name="workspace_role"), nullable=False, default=WorkspaceRole.VIEWER
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")
