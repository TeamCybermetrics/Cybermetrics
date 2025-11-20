from config.firebase import firebase_service
import threading

# auth related 
from infrastructure.auth_repository import AuthRepositoryFirebase 
from useCaseHelpers.auth_helper import AuthDomain
from services.auth_service import AuthService

# player search related
from infrastructure.player_repository import PlayerRepositoryFirebase
from useCaseHelpers.player_helper import PlayerDomain
from services.player_search_service import PlayerSearchService

# Singleton player repository instance (shared across all requests)
_player_repository_singleton: PlayerRepositoryFirebase | None = None
_player_repository_lock = threading.Lock()

def _get_player_repository_singleton() -> PlayerRepositoryFirebase:
    """Get or create the singleton player repository instance (thread-safe)."""
    global _player_repository_singleton
    
    # Double-checked locking pattern
    if _player_repository_singleton is None:
        with _player_repository_lock:
            # Check again after acquiring lock
            if _player_repository_singleton is None:
                _player_repository_singleton = PlayerRepositoryFirebase(firebase_service.db)
    
    return _player_repository_singleton

# roster average calculation related
from infrastructure.roster_repository import RosterRepositoryFirebase
from useCaseHelpers.roster_helper import RosterDomain
from services.roster_avg_service import RosterAvgService
from services.recommendation_service import RecommendationService

# saved player related
from infrastructure.saved_players_repository import SavedPlayersRepositoryFirebase
from useCaseHelpers.saved_players_helper import SavedPlayersDomain
from services.saved_players_service import SavedPlayersService

# auth related
def get_auth_repository():
    """Create Firebase auth repository instance"""
    return AuthRepositoryFirebase(firebase_service.db)

def get_auth_domain():
    """Create auth domain instance"""
    return AuthDomain()

def get_auth_service():
    """Create auth service instance"""
    auth_repo = get_auth_repository()
    auth_domain = get_auth_domain()
    return AuthService(auth_repo, auth_domain)

# player search related
def get_player_repository() -> PlayerRepositoryFirebase:
    """Get singleton Firebase player repository instance (for dependency injection)."""
    return _get_player_repository_singleton()

def get_player_domain():
    """Create player domain instance"""
    return PlayerDomain()

def get_player_search_service():
    """Create player search service instance"""
    player_repo = get_player_repository()
    player_domain = get_player_domain()
    return PlayerSearchService(player_repo, player_domain)

# roster avg related
def get_roster_repository():
    """Create Firebase roster repository instance"""
    player_repo = get_player_repository()
    return RosterRepositoryFirebase(firebase_service.db, player_repo)

def get_roster_domain() -> RosterDomain:
    """Create roster domain instance"""
    return RosterDomain()

def get_roster_avg_service():
    """Create roster average service instance"""
    roster_avg_repo = get_roster_repository()
    roster_avg_domain = get_roster_domain()
    player_repo = get_player_repository()
    return RosterAvgService(roster_avg_repo, roster_avg_domain, player_repo)

# rooster recomendation related
def get_recommendation_service() -> RecommendationService:
    """Create recommendation service instance."""
    roster_repo = get_roster_repository()
    roster_domain = get_roster_domain()
    player_repo = get_player_repository()
    player_domain = get_player_domain()
    return RecommendationService(roster_repo, roster_domain, player_repo, player_domain)

# save players related
def get_saved_players_repository():
    """Create Firebase saved players repository instance"""
    return SavedPlayersRepositoryFirebase(firebase_service.db)

def get_saved_players_domain() -> SavedPlayersDomain:
    """Create saved players domain instance"""
    return SavedPlayersDomain()

def get_saved_players_service():
    """Create saved players service instance"""
    saved_players_repo = get_saved_players_repository()
    saved_players_domain = get_saved_players_domain()
    return SavedPlayersService(saved_players_repo, saved_players_domain)


