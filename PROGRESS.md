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

## ⬜ Phase 2 — AI Content

- `campaigns`, `content_ideas`, `ai_generations`, `assets`, `posts`,
  `post_platforms` tables
- Real LLM adapter (OpenAI or Anthropic) behind `app/ai/providers/`
- Content agents (research → per-platform strategy → SEO → quality) per
  section 6, returning structured JSON
- Content Generator UI (section 37) wired to `/api/v1/content/generate`
- Content approval workflow (GENERATED → PENDING_REVIEW → APPROVED)

## ⬜ Phase 3 — Social Integration

- Instagram/Facebook/LinkedIn/YouTube OAuth + `SocialPublisher` adapters
- `social_accounts`, `oauth_tokens` tables (encrypted token storage)
- Social Accounts settings page

## ⬜ Phase 4 — Scheduler

- `scheduled_jobs`, `post_status_history` tables
- Celery Beat periodic tasks: publish due posts, retry with backoff
- Content Calendar UI (drag-and-drop)

## ⬜ Phase 5 — Analytics

- `post_metrics`, `metric_snapshots` tables; engagement-rate calculation
  service
- Analytics dashboard charts (Recharts), platform comparison, post
  performance page

## ⬜ Phase 6 — AI Growth

- `growth_insights`, `recommendations`, `content_scores` tables
- Growth agent, content score, weekly AI report
