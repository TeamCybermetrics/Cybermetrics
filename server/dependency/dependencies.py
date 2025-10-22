# auth related 
from infrastructure.auth_repository import AuthRepositoryFirebase 
from domain.auth_domain import AuthDomain
from services.auth_service import AuthService

# player search related
from infrastructure.player_repository import PlayerRepositoryFirebase
from domain.player_domain import PlayerDomain
from services.player_search_service import PlayerSearchService


# auth related
def get_auth_repository():
    """Create Firebase auth repository instance"""
    return AuthRepositoryFirebase()

def get_auth_domain():
    """Create auth domain instance"""
    return AuthDomain()

def get_auth_service():
    """Create auth service instance"""
    auth_repo = get_auth_repository()
    auth_domain = get_auth_domain()
    return AuthService(auth_repo, auth_domain)

# player search related
def get_player_repository():
    return PlayerRepositoryFirebase()

def get_player_domain():
    return PlayerDomain()

def get_player_search_service():
    player_repo = get_player_repository()
    player_domain = get_player_domain()
    return PlayerSearchService(player_repo, player_domain)