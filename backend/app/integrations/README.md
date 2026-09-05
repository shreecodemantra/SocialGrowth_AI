# Social Platform Integrations (Phase 3+)

Each subpackage (`instagram/`, `facebook/`, `linkedin/`, `youtube/`) will
implement the `SocialPublisher` interface (section 2 of the spec):

```python
class SocialPublisher:
    async def publish_text(self, post): ...
    async def publish_image(self, post): ...
    async def publish_video(self, post): ...
    async def get_post_metrics(self, external_post_id): ...
    async def delete_post(self, external_post_id): ...
```

Rules:
- Official platform APIs and OAuth 2.0 only — no browser automation/scraping.
- OAuth tokens are stored via the `oauth_tokens` table (encrypted at rest)
  and are never returned to the frontend.
- Every adapter must translate platform-specific HTTP errors (429, 401, 5xx)
  into the standardized error envelope from section 32, tagging `retryable`
  appropriately so the Celery publishing task can back off correctly.
