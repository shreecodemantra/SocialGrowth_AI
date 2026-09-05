"""
Import hub for Alembic autogenerate.

Every ORM model module must be imported here so `Base.metadata` is fully
populated before `alembic revision --autogenerate` inspects it. Add the
import as each new phase introduces new models.
"""
from app.db.base import Base  # noqa: F401

# Phase 1 — Foundation
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401
from app.models.workspace_member import WorkspaceMember  # noqa: F401
from app.models.brand_profile import BrandProfile  # noqa: F401

# Phase 2+ models are added here as they are implemented:
# from app.models.campaign import Campaign
# from app.models.content_idea import ContentIdea
# from app.models.ai_generation import AIGeneration
# from app.models.asset import Asset
# from app.models.post import Post
# from app.models.post_platform import PostPlatform
# from app.models.post_status_history import PostStatusHistory
# from app.models.post_metrics import PostMetrics
# from app.models.hashtag import Hashtag
# from app.models.content_score import ContentScore
# from app.models.growth_insight import GrowthInsight
# from app.models.recommendation import Recommendation
# from app.models.scheduled_job import ScheduledJob
# from app.models.tracked_link import TrackedLink
# from app.models.audit_log import AuditLog
