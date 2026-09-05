import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CampaignStatus, PlatformType, PostStatus


class CampaignCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    goal: str | None = None
    target_audience: list[str] = []  # empty => fall back to the brand profile's audience
    platforms: list[PlatformType] = Field(min_length=1)
    generate_images: bool = True
    # Video generation calls a paid, metered API (Veo) and can take minutes
    # to respond — off by default, matching the spec's Content Generator UI.
    generate_video: bool = False


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_type: str
    storage_url: str
    width: int | None
    height: int | None
    content_type: str


class PostPlatformOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform: PlatformType
    content: dict
    status: PostStatus
    quality_violations: list[str] = []
    external_post_id: str | None
    primary_asset: AssetOut | None = None


class PostPlatformUpdateRequest(BaseModel):
    content: dict


class StatusHistoryEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: PostStatus
    note: str | None
    created_at: datetime


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_id: str
    title: str
    status: PostStatus
    content_score: int | None
    campaign_id: uuid.UUID
    platforms: list[PostPlatformOut] = []
    status_history: list[StatusHistoryEntryOut] = []


class CampaignOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    goal: str | None
    platforms: list[str]
    generate_images: bool
    generate_video: bool
    status: CampaignStatus
    failure_reason: str | None
    created_at: datetime


class CampaignDetailOut(CampaignOut):
    posts: list[PostOut] = []
