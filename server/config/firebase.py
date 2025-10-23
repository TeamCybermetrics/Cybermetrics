import firebase_admin
from firebase_admin import credentials, firestore, auth
from .settings import settings

class FirebaseService:
    """Service for managing Firebase Admin SDK initialization and connections"""
    def __init__(self):
        """Initialize Firebase service and establish connection"""
        self.db = None
        self.auth = auth
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"Warning: Firebase initialization failed: {e}")
            print("Make sure to set up your Firebase credentials before running the server.")
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return self.db is not None

firebase_service = FirebaseService()

