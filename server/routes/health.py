from fastapi import APIRouter
from config.firebase import firebase_service

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint returning API information"""
    return {"message": "Cybermetrics API", "status": "running"}

@router.get("/health")
async def health_check():
    """Health check endpoint returning system status"""
    return {
        "status": "healthy",
        "firebase_connected": firebase_service.is_connected()
    }

