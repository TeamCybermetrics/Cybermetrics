"""
Unit tests for dependency injection functions.
"""
import pytest
from unittest.mock import Mock, patch
from dependency.dependencies import (
    get_auth_repository, get_auth_domain, get_auth_service,
    get_player_repository, get_player_domain, get_player_search_service,
    get_roster_repository, get_roster_domain, get_roster_avg_service,
    get_recommendation_service,
    get_saved_players_repository, get_saved_players_domain, get_saved_players_service
)


class TestAuthDependencies:
    """Tests for auth-related dependencies."""
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_auth_repository(self, mock_firebase_service):
        """Test get_auth_repository returns AuthRepositoryFirebase."""
        mock_firebase_service.db = Mock()
        
        repo = get_auth_repository()
        
        assert repo is not None
        assert hasattr(repo, 'db')
    
    @pytest.mark.unit
    def test_get_auth_domain(self):
        """Test get_auth_domain returns AuthDomain."""
        domain = get_auth_domain()
        
        assert domain is not None
        assert hasattr(domain, 'validate_signup_data')
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_auth_service(self, mock_firebase_service):
        """Test get_auth_service returns AuthService with dependencies."""
        mock_firebase_service.db = Mock()
        
        service = get_auth_service()
        
        assert service is not None
        assert hasattr(service, 'auth_repository')
        assert hasattr(service, 'auth_domain')


class TestPlayerDependencies:
    """Tests for player-related dependencies."""
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_player_repository(self, mock_firebase_service):
        """Test get_player_repository returns singleton."""
        mock_firebase_service.db = Mock()
        
        repo1 = get_player_repository()
        repo2 = get_player_repository()
        
        # Should be the same instance (singleton)
        assert repo1 is repo2
    
    @pytest.mark.unit
    def test_get_player_domain(self):
        """Test get_player_domain returns PlayerDomain."""
        domain = get_player_domain()
        
        assert domain is not None
        assert hasattr(domain, 'validate_search_query')
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_player_search_service(self, mock_firebase_service):
        """Test get_player_search_service returns PlayerSearchService."""
        mock_firebase_service.db = Mock()
        
        service = get_player_search_service()
        
        assert service is not None
        assert hasattr(service, 'player_repository')
        assert hasattr(service, 'player_domain')


class TestRosterDependencies:
    """Tests for roster-related dependencies."""
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_roster_repository(self, mock_firebase_service):
        """Test get_roster_repository returns RosterRepositoryFirebase."""
        mock_firebase_service.db = Mock()
        
        repo = get_roster_repository()
        
        assert repo is not None
    
    @pytest.mark.unit
    def test_get_roster_domain(self):
        """Test get_roster_domain returns RosterDomain."""
        domain = get_roster_domain()
        
        assert domain is not None
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_roster_avg_service(self, mock_firebase_service):
        """Test get_roster_avg_service returns RosterAvgService."""
        mock_firebase_service.db = Mock()
        
        service = get_roster_avg_service()
        
        assert service is not None
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_recommendation_service(self, mock_firebase_service):
        """Test get_recommendation_service returns RecommendationService."""
        mock_firebase_service.db = Mock()
        
        service = get_recommendation_service()
        
        assert service is not None


class TestSavedPlayersDependencies:
    """Tests for saved players dependencies."""
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_saved_players_repository(self, mock_firebase_service):
        """Test get_saved_players_repository returns SavedPlayersRepositoryFirebase."""
        mock_firebase_service.db = Mock()
        
        repo = get_saved_players_repository()
        
        assert repo is not None
        assert hasattr(repo, 'db')
    
    @pytest.mark.unit
    def test_get_saved_players_domain(self):
        """Test get_saved_players_domain returns SavedPlayersDomain."""
        domain = get_saved_players_domain()
        
        assert domain is not None
        assert hasattr(domain, 'validate_player_id')
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    def test_get_saved_players_service(self, mock_firebase_service):
        """Test get_saved_players_service returns SavedPlayersService."""
        mock_firebase_service.db = Mock()
        
        service = get_saved_players_service()
        
        assert service is not None
        assert hasattr(service, 'saved_players_repository')
        assert hasattr(service, 'saved_players_domain')


class TestPlayerRepositorySingleton:
    """Tests for player repository singleton pattern."""
    
    @pytest.mark.unit
    @patch('dependency.dependencies.firebase_service')
    @patch('dependency.dependencies._player_repository_singleton', None)
    def test_singleton_creates_once(self, mock_firebase_service):
        """Test that singleton is created only once."""
        mock_firebase_service.db = Mock()
        
        # Reset singleton
        import dependency.dependencies as deps
        deps._player_repository_singleton = None
        
        repo1 = get_player_repository()
        repo2 = get_player_repository()
        repo3 = get_player_repository()
        
        # All should be the same instance
        assert repo1 is repo2
        assert repo2 is repo3
