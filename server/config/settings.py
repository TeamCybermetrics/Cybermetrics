import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")
    FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")  # Required for password verification
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000"]
    
    def validate(self):
        """Validate critical configuration"""
        warnings = []
        
        if not self.FIREBASE_WEB_API_KEY:
            warnings.append("⚠️  FIREBASE_WEB_API_KEY is not set - authentication will not work!")
        
        if self.ENVIRONMENT == "production":
            if not self.FIREBASE_WEB_API_KEY:
                raise ValueError("FIREBASE_WEB_API_KEY must be set in production!")
            warnings.append("🔒 Running in PRODUCTION mode - ensure HTTPS is enabled!")
        
        return warnings

settings = Settings()

