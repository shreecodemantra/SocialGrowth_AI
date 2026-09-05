from fastapi import APIRouter

from app.api.v1 import auth, brands, users, workspaces

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(workspaces.router)
api_router.include_router(brands.router)

# Phase 2+ routers are wired in here as they are implemented:
# api_router.include_router(campaigns.router)
# api_router.include_router(content.router)
# api_router.include_router(assets.router)
# api_router.include_router(posts.router)
# api_router.include_router(scheduler.router)
# api_router.include_router(analytics.router)
# api_router.include_router(insights.router)
# api_router.include_router(recommendations.router)
# api_router.include_router(tracking.router)
# api_router.include_router(social_accounts.router)
