"""Shared helpers used by multiple agents. Not part of the public agent API."""
import json
import re

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


class JSONExtractionError(ValueError):
    pass


def extract_json(text: str) -> dict:
    """
    Pull the first {...} block out of an LLM response and parse it. Real
    models reliably return exactly this when instructed to; the mock
    provider's canned text does not, so callers must catch
    `JSONExtractionError` and fall back to a deterministic default — see
    each agent's `_fallback_*` function.
    """
    match = _JSON_BLOCK_RE.search(text)
    if not match:
        raise JSONExtractionError(f"No JSON object found in LLM response: {text[:200]!r}")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise JSONExtractionError(f"LLM response was not valid JSON: {exc}") from exc
