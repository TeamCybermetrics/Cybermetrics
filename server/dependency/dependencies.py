from config.firebase import firebase_service

# auth related 
from infrastructure.auth_repository import AuthRepositoryFirebase 
from domain.auth_domain import AuthDomain
from services.auth_service import AuthService

# player search related
from infrastructure.player_repository import PlayerRepositoryFirebase
from domain.player_domain import PlayerDomain
from services.player_search_service import PlayerSearchService

# roster average calculation related
from infrastructure.roster_repository import RosterRepositoryFirebase
from domain.roster_domain import RosterDomain
from services.roster_avg_service import RosterAvgService

# saved player related
from infrastructure.saved_players_repository import SavedPlayersRepositoryFirebase
from domain.saved_players_domain import SavedPlayersDomain
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
def get_player_repository():
    return PlayerRepositoryFirebase(firebase_service.db)

def get_player_domain():
    return PlayerDomain()

def get_player_search_service():
    player_repo = get_player_repository()
    player_domain = get_player_domain()
    return PlayerSearchService(player_repo, player_domain)

# roster avg related
def get_roster_repository():
    return RosterRepositoryFirebase(firebase_service.db)

def get_roster_domain() -> RosterDomain:
    return RosterDomain()

def get_roster_avg_service():
    roster_avg_repo = get_roster_repository()
    rooster_avg_domain = get_roster_domain()
    return RosterAvgService(roster_avg_repo, roster_avg_domain)

# save players related
def get_saved_players_repository():
    return SavedPlayersRepositoryFirebase(firebase_service.db)

def get_saved_players_domain() -> SavedPlayersDomain:
    return SavedPlayersDomain()

def get_saved_players_service():
    saved_players_repo = get_saved_players_repository()
    saved_players_domain = get_saved_players_domain()
    return SavedPlayersService(saved_players_repo, saved_players_domain)


