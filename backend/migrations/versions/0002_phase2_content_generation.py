"""Phase 2 content generation: campaigns, posts, post_platforms, assets, post_status_history, ai_generations

Revision ID: 0002_phase2_content_generation
Revises: 0001_phase1_foundation
Create Date: 2026-09-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_phase2_content_generation"
down_revision: Union[str, None] = "0001_phase1_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum(name: str, values: list[str]) -> postgresql.ENUM:
    enum_type = postgresql.ENUM(*values, name=name, create_type=True)
    enum_type.create(op.get_bind(), checkfirst=True)
    return enum_type


def upgrade() -> None:
    _create_enum("campaign_status", ["DRAFT", "GENERATING", "READY", "FAILED"])
    post_status_values = [
        "DRAFT", "GENERATING", "GENERATED", "PENDING_REVIEW", "APPROVED",
        "SCHEDULED", "PUBLISHING", "PUBLISHED", "FAILED", "CANCELLED",
    ]
    _create_enum("post_status", post_status_values)
    _create_enum("post_platform_status", post_status_values)
    _create_enum("post_status_history_status", post_status_values)
    _create_enum("platform_type", ["INSTAGRAM", "FACEBOOK", "LINKEDIN", "YOUTUBE"])
    _create_enum("asset_type", ["IMAGE", "VIDEO", "THUMBNAIL"])

    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("goal", sa.String(length=255), nullable=True),
        sa.Column("target_audience", sa.JSON(), nullable=False),
        sa.Column("platforms", sa.JSON(), nullable=False),
        sa.Column("generate_images", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("generate_video", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", postgresql.ENUM(name="campaign_status", create_type=False), nullable=False),
        sa.Column("failure_reason", sa.String(length=1000), nullable=True),
    )
    op.create_index("ix_campaigns_workspace_id", "campaigns", ["workspace_id"])

    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_id", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("status", postgresql.ENUM(name="post_status", create_type=False), nullable=False),
        sa.Column("content_score", sa.Integer(), nullable=True),
        sa.UniqueConstraint("workspace_id", "display_id", name="uq_posts_workspace_display_id"),
    )
    op.create_index("ix_posts_workspace_id", "posts", ["workspace_id"])

    op.create_table(
        "post_platforms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", postgresql.ENUM(name="platform_type", create_type=False), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("status", postgresql.ENUM(name="post_platform_status", create_type=False), nullable=False),
        sa.Column("quality_violations", sa.JSON(), nullable=False),
        sa.Column("primary_asset_id", postgresql.UUID(as_uuid=True), nullable=True),  # FK added after `assets` exists
        sa.Column("external_post_id", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("post_id", "platform", name="uq_post_platforms_post_platform"),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("post_platform_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("post_platforms.id", ondelete="CASCADE"), nullable=True),
        sa.Column("asset_type", postgresql.ENUM(name="asset_type", create_type=False), nullable=False),
        sa.Column("storage_url", sa.String(length=1000), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False, server_default="image/png"),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("generation_prompt", sa.String(length=4000), nullable=True),
    )
    op.create_index("ix_assets_workspace_id", "assets", ["workspace_id"])

    op.create_foreign_key(
        "fk_post_platforms_primary_asset_id", "post_platforms", "assets", ["primary_asset_id"], ["id"], ondelete="SET NULL"
    )

    op.create_table(
        "post_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", postgresql.ENUM(name="post_status_history_status", create_type=False), nullable=False),
        sa.Column("note", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_post_status_history_post_id", "post_status_history", ["post_id"])

    op.create_table(
        "ai_generations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("post_platform_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("post_platforms.id", ondelete="CASCADE"), nullable=True),
        sa.Column("agent_name", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("raw_response", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_generations_workspace_id", "ai_generations", ["workspace_id"])


def downgrade() -> None:
    op.drop_table("ai_generations")
    op.drop_table("post_status_history")
    op.drop_constraint("fk_post_platforms_primary_asset_id", "post_platforms", type_="foreignkey")
    op.drop_table("assets")
    op.drop_table("post_platforms")
    op.drop_table("posts")
    op.drop_table("campaigns")

    for enum_name in [
        "asset_type", "platform_type", "post_status_history_status",
        "post_platform_status", "post_status", "campaign_status",
    ]:
        postgresql.ENUM(name=enum_name).drop(op.get_bind(), checkfirst=True)
