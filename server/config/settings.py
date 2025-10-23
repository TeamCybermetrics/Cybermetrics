import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Loads and set configuration value for application"""
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000"]
    
settings = Settings()

