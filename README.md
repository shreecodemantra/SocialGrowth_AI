# SocialGrowth AI

AI Social Media Content Automation & Analytics Platform. First workspace:
**Shree Code Mantra**.

This repo is built in phases (see [`PROGRESS.md`](./PROGRESS.md)). **Phase 1
— Foundation** is complete: authentication, workspaces, brand profiles, and
the full project scaffolding the later phases plug into.

## Architecture

```
backend/     FastAPI + SQLAlchemy 2.x (async) + Alembic + Celery
frontend/    React + Vite + TypeScript + Tailwind + TanStack Query
nginx/       Reverse proxy config for the docker-compose stack
```

See `backend/app/` for the module layout: `api/` (routes) → `services/`
(business logic) → `repositories/` (data access) → `models/` (ORM). AI
providers live in `app/ai/` behind provider-agnostic interfaces; social
platform adapters land in `app/integrations/` in Phase 3; the agent pipeline
lands in `app/agents/` in Phase 2.

## Running the application

There are two ways to run the whole stack. Docker Compose is the fastest
path to "it's up"; running natively is better while actively developing the
backend or frontend (hot reload, debugger, no rebuilds).

### Option A — Docker Compose (everything, one command)

```bash
cp backend/.env.example backend/.env
```

The example file already points `DATABASE_URL`/`REDIS_URL` at the
`postgres`/`redis` service *names*, which only resolve inside the compose
network — that's correct as-is for this option, leave them unchanged.

```bash
docker compose up --build
```

This starts `postgres`, `redis`, `backend`, `celery_worker`, `celery_beat`,
`frontend`, and the top-level `nginx` reverse proxy. **The database schema
is not created automatically** — the first time (and after pulling new
migrations), apply them once the containers are up:

```bash
docker compose exec backend alembic upgrade head
```

| Service | URL |
|---|---|
| Whole app (nginx → frontend + `/api`) | http://localhost |
| Backend directly (Swagger docs at `/docs`) | http://localhost:8000 |
| Frontend container directly (bypasses nginx) | http://localhost:5173 |

Check it's healthy: `curl http://localhost/health` should return
`{"status":"ok",...}`. Then open http://localhost and register an account
(see the walkthrough below).

Useful commands:

```bash
docker compose logs -f backend        # tail one service's logs
docker compose restart backend        # after editing backend/.env
docker compose down                   # stop everything, keep data
docker compose down -v                # stop everything AND wipe the Postgres volume
```

### Option B — Run natively (backend + frontend on your machine)

Postgres and Redis are still easiest to run via Docker even in this mode;
only the app code runs natively so you get hot reload.

```bash
docker compose up -d postgres redis
```

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and change the two Postgres/Redis hostnames from the
docker-network names to `localhost`, since nothing here runs inside that
network:

```
DATABASE_URL=postgresql+asyncpg://socialgrowth:socialgrowth@localhost:5432/socialgrowth
SYNC_DATABASE_URL=postgresql+psycopg2://socialgrowth:socialgrowth@localhost:5432/socialgrowth
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

Then apply migrations and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Backend is now at http://localhost:8000 (docs at `/docs`). Run the test
suite any time (uses an in-memory SQLite DB — no Postgres/Redis needed for
this):

```bash
pytest -v
```

To also run the scheduler (only matters once Phase 4 adds real periodic
tasks — safe to skip for now), in separate terminals with the same venv
activated:

```bash
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

**Frontend** (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server proxies `/api` to
`http://localhost:8000` by default (see `vite.config.ts`; override with
`VITE_API_PROXY_TARGET` in `frontend/.env` if the backend runs elsewhere).

## First-run walkthrough (current MVP scope)

1. Open the app — http://localhost (Docker Compose) or http://localhost:5173
   (native) — and register an account at `/register`.
2. You're redirected to `/dashboard`; create a workspace (e.g. "Shree Code
   Mantra").
3. Open **Brand Settings** and fill in the brand profile — the content
   pipeline reads this every time it generates or scores content, and
   generation is blocked with a clear error until it's set up.
4. Open **Content Generator**, enter a topic (e.g. "Transforming Students
   into Industry-Ready Developers"), pick platforms, and generate. Review
   each platform's content, edit/regenerate/approve/reject per platform.
   Generated campaigns/posts are listed under **Campaigns**.
5. Everything else in the sidebar (Calendar, Posts, Analytics, Insights,
   Recommendations, Social Accounts, Team, Settings) shows a "coming in
   Phase N" placeholder until that phase lands — there's no way to actually
   *publish* an approved post yet (see `PROGRESS.md`, Phase 3).

## Using Gemini for image & reel generation

The image and video providers can be switched from the zero-cost mock
implementation to real Gemini output without touching any business logic —
that's the point of the `ImageProvider`/`VideoProvider` abstraction:

1. Get a key at https://aistudio.google.com/apikey.
2. In `backend/.env`, set:
   ```
   IMAGE_PROVIDER=gemini
   VIDEO_PROVIDER=gemini
   GEMINI_API_KEY=your-key-here
   ```
3. Restart the backend (`docker compose up --build backend` or your local
   `uvicorn` process).

Defaults: images use `gemini-2.5-flash-image` ("Nano Banana"); reels use
`veo-3.1-fast-generate-preview` (9:16, portrait, for Reels/Shorts). Both are
configurable via `GEMINI_IMAGE_MODEL` / `GEMINI_VIDEO_MODEL`. Note Veo is a
paid, metered API (billed per output-second, no free tier) — image
generation has a free tier. See `app/ai/providers/gemini.py` for details;
`get_image_provider()`/`get_video_provider()` in `app/ai/factory.py` raise a
clear error if the provider is set to `gemini` without a key configured.

## Design principles carried through every phase

- **Provider-agnostic AI**: business logic depends on `LLMProvider` /
  `ImageProvider` / `VideoProvider` interfaces (`app/ai/base.py`), never a
  vendor SDK directly.
- **Official APIs only** for social publishing — no scraping or browser
  automation (`app/integrations/README.md`).
- **No fake engagement** — the platform never fabricates followers, likes,
  or engagement, and never guarantees virality (spec section 42).
- **Human approval required** before anything publishes — no AI-generated
  content goes out without an explicit approve/schedule step.
- **Layered architecture**: routes stay thin; all business logic lives in
  `services/`, all queries in `repositories/`.
