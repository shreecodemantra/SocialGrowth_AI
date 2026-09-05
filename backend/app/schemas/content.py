"""
Per-platform content shapes (spec section 5). Each platform gets a
dedicated schema — the content agent never just copies one platform's
output into another.
"""
from pydantic import BaseModel


class InstagramContent(BaseModel):
    caption: str
    hook: str
    cta: str
    hashtags: list[str]
    image_prompt: str
    alt_text: str
    reel_idea: str


class LinkedInContent(BaseModel):
    hook: str
    post: str
    cta: str
    hashtags: list[str]
    image_prompt: str


class FacebookContent(BaseModel):
    post: str
    cta: str
    hashtags: list[str]
    image_prompt: str


class YouTubeContent(BaseModel):
    video_title: str
    description: str
    tags: list[str]
    keywords: list[str]
    thumbnail_text: str
    thumbnail_prompt: str
    shorts_script: str
    longform_script: str


PLATFORM_CONTENT_SCHEMAS: dict[str, type[BaseModel]] = {
    "INSTAGRAM": InstagramContent,
    "LINKEDIN": LinkedInContent,
    "FACEBOOK": FacebookContent,
    "YOUTUBE": YouTubeContent,
}
