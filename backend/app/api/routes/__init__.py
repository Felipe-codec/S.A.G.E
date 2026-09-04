from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.imap_configs import router as imap_router
from app.api.routes.steam_accounts import router as steam_router
from app.api.routes.tokens import router as tokens_router
from app.api.routes.redemption import router as redemption_router

__all__ = [
    "health_router",
    "auth_router",
    "imap_router",
    "steam_router",
    "tokens_router",
    "redemption_router",
]
