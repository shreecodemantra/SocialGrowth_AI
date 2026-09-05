import uuid

from pydantic import BaseModel, ConfigDict


class BrandProfileUpsert(BaseModel):
    brand_name: str
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    target_audience: list[str] = []
    target_countries: list[str] = []
    target_languages: list[str] = []
    brand_tone: str | None = None
    brand_keywords: list[str] = []
    forbidden_words: list[str] = []
    cta_style: str | None = None
    preferred_hashtags: list[str] = []
    logo_url: str | None = None
    brand_colors: list[str] = []


class BrandProfileOut(BrandProfileUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
