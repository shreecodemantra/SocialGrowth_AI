# SocialGrowth AI — Build Progress

Tracks the phased roadmap from the spec (section 43). Update this as each
phase lands.

## ✅ Phase 1 — Foundation (done)

- FastAPI backend, async SQLAlchemy 2.x models, Alembic migrations
- PostgreSQL schema: `users`, `workspaces`, `workspace_members`, `brand_profiles`
- JWT auth (access + refresh tokens), bcrypt password hashing
- Role-based workspace membership (OWNER/ADMIN/EDITOR/VIEWER) enforced via
  FastAPI dependencies
- Brand profile CRUD, scoped per workspace
- Structured (structlog) logging with request/user/workspace context and
  automatic secret redaction
- Standardized error envelope (`{success, error: {code, message, retryable}}`)
- AI provider abstraction (`LLMProvider` / `ImageProvider` / `VideoProvider`)
  with a mock implementation so the app runs with zero vendor API keys
- **Gemini image & video (reel) provider wired** (`app/ai/providers/gemini.py`):
  set `IMAGE_PROVIDER=gemini` / `VIDEO_PROVIDER=gemini` + `GEMINI_API_KEY` in
  `backend/.env`. Images use Gemini 2.5 Flash Image ("Nano Banana") by
  default (an `imagen-*` model id also works); reels use Veo 3.1. See
  `backend/.env.example` for all `GEMINI_*` settings.
- Object storage service (S3/R2-compatible via boto3) — wired, unused until
  Phase 2 needs to persist generated assets
- Celery app wired (broker/backend configured) with an empty beat schedule —
  actual tasks land in Phase 4
- React + Vite + TS + Tailwind frontend: login/register, workspace creation,
  brand profile editor, dashboard shell with the full section-36 sidebar
  (non-Phase-1 links show a "coming in Phase N" placeholder)
- Docker Compose stack: postgres, redis, backend, celery_worker, celery_beat,
  frontend, nginx
- GitHub Actions CI: backend pytest suite (SQLite in-memory, no external
  services) + frontend typecheck/build
- Backend test suite passing (7/7): registration, login, duplicate-email
  rejection, wrong-password rejection, `/users/me` auth guard, workspace
  creation + brand profile upsert, cross-workspace permission denial

## ✅ Phase 2 — AI Content (done)

- Tables: `campaigns`, `posts`, `post_platforms`, `assets`, `post_status_history`, `ai_generations`
- Agent pipeline (`app/agents/`), each a plain async function taking
  structured input and returning structured JSON — no DB/HTTP calls inside
  an agent itself:
  - `research_agent` — grounds the pipeline with a brief before any platform writing starts
  - `content_agent` — dedicated prompt + schema per platform (Instagram/LinkedIn/Facebook/YouTube
    never share content — see `app/schemas/content.py`)
  - `seo_agent` — merges brand-preferred hashtags, dedupes, caps per-platform counts
  - `quality_agent` — flags forbidden-word violations for the reviewer (never silently blocks)
  - `image_agent` — resolves per-platform creative dimensions, builds the prompt, calls `ImageProvider`
  - All four fall back to a deterministic, still-useful default when the configured LLM
    doesn't return parseable JSON — true today for `LLM_PROVIDER=mock` (the default), so the
    whole pipeline runs end-to-end with zero AI keys configured. Swap in a real `LLMProvider`
    (OpenAI/Anthropic/Gemini text) any time — no other code changes.
- `CampaignService` orchestrates: create campaign → research once → per
  platform generate+SEO+quality(+image, +video if requested for
  Instagram/YouTube) → `PENDING_REVIEW`. Failures leave the campaign/post
  rows marked `FAILED` with a reason rather than disappearing.
- Approval workflow: approve/reject per platform, edit content (re-runs SEO
  + quality, resets to `PENDING_REVIEW` even if previously approved),
  regenerate a single platform. Post-level status flips to `APPROVED` once
  every platform is.
- `LocalStorageService` fallback (`app/services/storage_service.py`,
  served at `/media`) so generated images work without real S3/R2
  credentials — used automatically whenever they're unset; same interface
  as the real `StorageService`, swap is transparent to callers.
- Content Generator UI (section 37): topic + goal + platform picker +
  image/video toggles → generates → per-platform review cards (image,
  every field, hashtags as chips, quality-violation banner,
  Edit/Regenerate/Approve/Reject). Campaigns list + detail pages reuse the
  same review card.
- 19 new backend tests (25/25 total): agent-level unit tests (fallback
  behavior, hashtag merging/capping, forbidden-word detection) +
  full-pipeline API tests (generation, brand-profile-required guard,
  approval/rejection/edit/regenerate, cross-workspace permission denial)

## ⬜ Phase 3 — Social Integration

- Instagram/Facebook/LinkedIn/YouTube OAuth + `SocialPublisher` adapters
- `social_accounts`, `oauth_tokens` tables (encrypted token storage)
- Social Accounts settings page
- Actually publishing an approved post is still not possible until this phase lands

## ⬜ Phase 4 — Scheduler

- `scheduled_jobs` table
- Celery Beat periodic tasks: publish due posts, retry with backoff
- Content Calendar UI (drag-and-drop)
- Move campaign generation (and especially video generation, which can take
  minutes) off the request/response cycle and onto a Celery task

## ⬜ Phase 5 — Analytics

- `post_metrics`, `metric_snapshots` tables; engagement-rate calculation
  service
- Analytics dashboard charts (Recharts), platform comparison, post
  performance page

## ⬜ Phase 6 — AI Growth

- `growth_insights`, `recommendations`, `content_scores` tables
- Growth agent, content score, weekly AI report
