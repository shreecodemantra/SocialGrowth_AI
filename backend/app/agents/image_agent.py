"""
Image Agent (spec sections 6-7): resolves the platform-appropriate creative
dimensions, builds a prompt that folds in brand visual guidance, calls the
configured ImageProvider, and persists the result to object storage.
Callers (CampaignService) are responsible for writing the resulting URL to
an `assets` row — this module never touches the database.
"""
from dataclasses import dataclass

from app.ai.base import ImageProvider
from app.core.logging import get_logger
from app.models.brand_profile import BrandProfile
from app.models.enums import PlatformType
from app.services.storage_service import StorageService

logger = get_logger(__name__)

AGENT_NAME = "image_agent"


@dataclass
class GeneratedAsset:
    storage_url: str
    width: int
    height: int
    content_type: str
    prompt: str


# (width, height) per platform's primary feed creative (spec section 7).
_DIMENSIONS: dict[PlatformType, tuple[int, int]] = {
    PlatformType.INSTAGRAM: (1080, 1350),  # 4:5 feed portrait
    PlatformType.LINKEDIN: (1200, 627),  # ~1.91:1 feed graphic
    PlatformType.FACEBOOK: (1200, 630),  # feed graphic
    PlatformType.YOUTUBE: (1280, 720),  # 16:9 thumbnail
}


def dimensions_for(platform: PlatformType) -> tuple[int, int]:
    return _DIMENSIONS[platform]


def _image_prompt_from_content(platform: PlatformType, content: dict, brand: BrandProfile) -> str:
    base_prompt = content.get("image_prompt") or content.get("thumbnail_prompt") or ""
    width, height = dimensions_for(platform)

    return f"""{base_prompt}

Brand: {brand.brand_name} ({brand.industry or "technology"}).
Brand colors: {", ".join(brand.brand_colors) or "use a clean, modern professional palette"}.
Style: {brand.brand_tone or "clean, modern, professional"}, strong visual hierarchy, legible typography,
no misspelled words, dimensions {width}x{height}."""


async def generate_for_platform(
    image_provider: ImageProvider,
    storage: StorageService,
    brand: BrandProfile,
    content: dict,
    platform: PlatformType,
) -> GeneratedAsset:
    width, height = dimensions_for(platform)
    prompt = _image_prompt_from_content(platform, content, brand)

    logger.info("image_agent_generate", platform=platform.value, width=width, height=height)
    result = await image_provider.generate(prompt, width=width, height=height)

    storage_url = storage.upload_bytes(
        result.image_bytes, content_type=result.content_type, key_prefix=f"assets/{platform.value.lower()}"
    )

    return GeneratedAsset(
        storage_url=storage_url,
        width=width,
        height=height,
        content_type=result.content_type,
        prompt=prompt,
    )
