"""
Quality Agent (spec section 6): a brand-safety gate before content reaches
the approval queue. Flags — but does not silently strip — any use of the
brand's forbidden words/phrases (spec section 4) so a human reviewer sees
exactly why a post needs a second look.
"""
from app.models.brand_profile import BrandProfile
from app.schemas.agents import QualityCheckResult


def _all_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str)]
    return []


def check_content(content: dict, brand: BrandProfile) -> QualityCheckResult:
    if not brand.forbidden_words:
        return QualityCheckResult(passed=True, violations=[])

    violations: list[str] = []
    forbidden_lower = [w.lower() for w in brand.forbidden_words if w.strip()]

    for field, value in content.items():
        for text in _all_strings(value):
            text_lower = text.lower()
            for forbidden, original in zip(forbidden_lower, brand.forbidden_words):
                if forbidden in text_lower:
                    violations.append(f"{field}: contains forbidden phrase '{original}'")

    return QualityCheckResult(passed=len(violations) == 0, violations=violations)
