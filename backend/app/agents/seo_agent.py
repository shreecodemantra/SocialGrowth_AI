"""
SEO Agent (spec section 6): normalizes and enriches hashtags/keywords after
content generation — merges in the brand's preferred hashtags, dedupes,
normalizes formatting, and caps counts to what each platform actually
rewards (Instagram tolerates many hashtags; LinkedIn and Facebook do not).
"""
from app.models.brand_profile import BrandProfile
from app.models.enums import PlatformType

_HASHTAG_CAPS = {
    PlatformType.INSTAGRAM: 25,
    PlatformType.LINKEDIN: 5,
    PlatformType.FACEBOOK: 8,
}


def _normalize_hashtag(tag: str) -> str:
    tag = tag.strip()
    if not tag:
        return ""
    if not tag.startswith("#"):
        tag = f"#{tag}"
    return "#" + "".join(ch for ch in tag[1:] if ch.isalnum() or ch == "_")


def _dedupe_case_insensitive(tags: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for tag in tags:
        key = tag.lower()
        if key and key not in seen:
            seen.add(key)
            result.append(tag)
    return result


def enrich_hashtags(content: dict, brand: BrandProfile, platform: PlatformType) -> dict:
    enriched = dict(content)

    if platform in (PlatformType.INSTAGRAM, PlatformType.LINKEDIN, PlatformType.FACEBOOK):
        combined = [_normalize_hashtag(t) for t in (enriched.get("hashtags", []) + brand.preferred_hashtags)]
        combined = _dedupe_case_insensitive([t for t in combined if t])
        enriched["hashtags"] = combined[: _HASHTAG_CAPS[platform]]

    elif platform == PlatformType.YOUTUBE:
        tags = _dedupe_case_insensitive([t.strip() for t in enriched.get("tags", []) + brand.brand_keywords if t.strip()])
        keywords = _dedupe_case_insensitive(
            [k.strip() for k in enriched.get("keywords", []) + brand.brand_keywords if k.strip()]
        )
        enriched["tags"] = tags[:15]
        enriched["keywords"] = keywords[:10]

    return enriched
