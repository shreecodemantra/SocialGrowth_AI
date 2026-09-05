"""Phase 1 foundation: users, workspaces, workspace_members, brand_profiles

Revision ID: 0001_phase1_foundation
Revises:
Create Date: 2026-09-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_phase1_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    )
    op.create_index("ix_workspaces_slug", "workspaces", ["slug"], unique=True)

    workspace_role_enum = postgresql.ENUM(
        "OWNER", "ADMIN", "EDITOR", "VIEWER", name="workspace_role", create_type=True
    )
    workspace_role_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "workspace_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", postgresql.ENUM("OWNER", "ADMIN", "EDITOR", "VIEWER", name="workspace_role", create_type=False), nullable=False),
        sa.UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member_workspace_user"),
    )

    op.create_table(
        "brand_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("target_audience", sa.JSON(), nullable=False),
        sa.Column("target_countries", sa.JSON(), nullable=False),
        sa.Column("target_languages", sa.JSON(), nullable=False),
        sa.Column("brand_tone", sa.String(length=255), nullable=True),
        sa.Column("brand_keywords", sa.JSON(), nullable=False),
        sa.Column("forbidden_words", sa.JSON(), nullable=False),
        sa.Column("cta_style", sa.String(length=255), nullable=True),
        sa.Column("preferred_hashtags", sa.JSON(), nullable=False),
        sa.Column("logo_url", sa.String(length=1000), nullable=True),
        sa.Column("brand_colors", sa.JSON(), nullable=False),
        sa.UniqueConstraint("workspace_id", name="uq_brand_profiles_workspace_id"),
    )


def downgrade() -> None:
    op.drop_table("brand_profiles")
    op.drop_table("workspace_members")
    postgresql.ENUM(name="workspace_role").drop(op.get_bind(), checkfirst=True)
    op.drop_index("ix_workspaces_slug", table_name="workspaces")
    op.drop_table("workspaces")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
