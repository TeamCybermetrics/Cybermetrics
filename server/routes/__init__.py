from .auth import router as auth_router
from .health import router as health_router
from .players import router as players_router
from .recommendations import router as recommendations_router

__all__ = ["auth_router", "health_router", "players_router", "recommendations_router"]

