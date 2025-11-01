import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Loads and set configuration value for application"""
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "./serviceAccountKey.json")
    FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")  # Required for password verification
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, staging, production
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000"]
    
    # Rate Limiting & Proxy
    TRUST_PROXY = os.getenv("TRUST_PROXY", "false").lower() == "true"  # Only enable if behind trusted reverse proxy
    
    def validate(self):
        """
        Validate configuration and collect startup warnings.
        
        Checks for missing or insecure settings and returns user-facing warning messages.
        Specifically, it warns when FIREBASE_WEB_API_KEY is not set and adds a production-mode
        warning advising HTTPS. If running in production and FIREBASE_WEB_API_KEY is absent,
        validation fails.
        
        Returns:
            list[str]: List of warning messages; empty if no warnings.
        
        Raises:
            ValueError: If ENVIRONMENT is "production" and FIREBASE_WEB_API_KEY is not set.
        """
        warnings = []
        
        if not self.FIREBASE_WEB_API_KEY:
            warnings.append("⚠️  FIREBASE_WEB_API_KEY is not set - authentication will not work!")
        
        if self.ENVIRONMENT == "production":
            if not self.FIREBASE_WEB_API_KEY:
                raise ValueError("FIREBASE_WEB_API_KEY must be set in production!")
            warnings.append("🔒 Running in PRODUCTION mode - ensure HTTPS is enabled!")
        
        return warnings

settings = Settings()
