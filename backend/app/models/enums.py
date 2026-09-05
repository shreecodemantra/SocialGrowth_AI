"""Shared enums used across Phase 2 models."""
import enum


class PlatformType(str, enum.Enum):
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    LINKEDIN = "LINKEDIN"
    YOUTUBE = "YOUTUBE"


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    READY = "READY"
    FAILED = "FAILED"


class PostStatus(str, enum.Enum):
    """Per spec section 11. Applies to both `posts` (overall) and each
    `post_platforms` row (a platform can be independently approved/published
    while siblings are still pending)."""

    DRAFT = "DRAFT"
    GENERATING = "GENERATING"
    GENERATED = "GENERATED"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AssetType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    THUMBNAIL = "THUMBNAIL"
