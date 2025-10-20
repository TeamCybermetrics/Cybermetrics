from infrastructure.auth_repository import AuthRepositoryFirebase  
from domain.auth_domain import AuthDomain
from services.auth_service import AuthService

def get_auth_repository():
    """Create Firebase auth repository instance"""
    return AuthRepositoryFirebase()  # ← Use correct class name

def get_auth_domain():
    """Create auth domain instance"""
    return AuthDomain()

def get_auth_service():
    """Create auth service instance"""
    auth_repo = get_auth_repository()
    auth_domain = get_auth_domain()
    return AuthService(auth_repo, auth_domain)