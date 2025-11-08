from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from routes import auth_router, health_router, players_router, team_builder_router
from middleware.rate_limit import RateLimitMiddleware, rate_limiter
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Validate configuration
    """
    Manage the application's lifespan by running startup configuration validation and printing startup/shutdown messages.
    
    On startup, validates application settings and prints any warnings or a success message, then logs environment and server address. Yields control to allow the application to run. On shutdown, prints a shutdown message.
    
    Parameters:
        app (FastAPI): The FastAPI application instance whose lifespan this context manager controls.
    
    Returns:
        asynccontextmanager: An async context manager that performs the described startup and shutdown actions.
    """
    print("\n" + "="*50)
    print("🚀 Starting Cybermetrics API")
    print("="*50)
    
    warnings = settings.validate()
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("✅ All configuration validated successfully")
    
    print("="*50)
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🚀 Server running at http://{settings.HOST}:{settings.PORT}")
    print(f"🔒 Proxy trust mode: {'ENABLED' if settings.TRUST_PROXY else 'DISABLED'}")
    print("="*50 + "\n")
    
    # Start rate limiter cleanup task
    print("🧹 Starting rate limiter cleanup task...")
    rate_limiter.start_cleanup_task()
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down Cybermetrics API...")
    print("🧹 Stopping rate limiter cleanup task...")
    await rate_limiter.stop_cleanup_task()
    print("✅ Cleanup complete\n")

# Initialize FastAPI app
app = FastAPI(title="Cybermetrics API", lifespan=lifespan)

# Add rate limiting middleware (before CORS)
app.add_middleware(RateLimitMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(players_router)
app.include_router(team_builder_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
