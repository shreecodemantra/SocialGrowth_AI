# Agents (Phase 2+)

This package will hold the content pipeline agents described in the platform
spec section 6:

```
campaign_agent.py     - kicks off a campaign from a title/topic
research_agent.py      - gathers topic context to ground generation
content_agent.py       - dispatches to per-platform content strategies
image_agent.py         - builds platform-specific image prompts + calls ImageProvider
seo_agent.py            - keyword/hashtag optimization
quality_agent.py        - brand-safety + forbidden-word checks before approval queue
growth_agent.py          - Phase 6: analyzes historical metrics, produces insights/recommendations
```

Each agent should be a plain async class/function that takes structured
input (e.g. a `BrandProfile` + `ContentIdea`) and returns structured JSON —
no direct DB or HTTP calls; those belong in services/repositories so agents
stay testable in isolation with mocked `LLMProvider`/`ImageProvider`.
