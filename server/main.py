from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from routes import auth_router, health_router, players_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Validate configuration
    print("\n" + "="*50)
    print("🚀 Starting Cybermetrics API")
    print("="*50)
    
    warnings = settings.validate()
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("✅ All configuration validated successfully")
    
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 Server: {settings.HOST}:{settings.PORT}")
    print("="*50 + "\n")
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down Cybermetrics API\n")

# Initialize FastAPI app
app = FastAPI(title="Cybermetrics API", lifespan=lifespan)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
