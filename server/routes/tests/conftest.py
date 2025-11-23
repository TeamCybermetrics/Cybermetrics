"""
Pytest configuration and shared fixtures for the Cybermetrics backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import os
import sys

# Add the server directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables for the entire test session."""
    os.environ["FIREBASE_CREDENTIALS_PATH"] = "./test_serviceAccountKey.json"
    os.environ["FIREBASE_WEB_API_KEY"] = "test_api_key"
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "8000"


@pytest.fixture
def mock_firebase_credentials(monkeypatch):
    """Mock Firebase credentials to avoid requiring actual credentials during tests."""
    monkeypatch.setenv("FIREBASE_CREDENTIALS_PATH", "./test_serviceAccountKey.json")
    monkeypatch.setenv("FIREBASE_WEB_API_KEY", "test_api_key")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    
    # Mock firebase_admin to prevent actual Firebase initialization
    with patch('firebase_admin.initialize_app'), \
         patch('firebase_admin.get_app'):
        yield


@pytest.fixture
def client(mock_firebase_credentials):
    """
    Create a TestClient for the FastAPI application.
    This fixture provides a test client that can be used to make requests to the API.
    """
    # Mock Firebase service and player repository to avoid initialization issues
    with patch('config.firebase.firebase_service') as mock_firebase, \
         patch('dependency.dependencies.get_player_repository') as mock_get_repo:
        
        # Configure Firebase service mock
        mock_firebase.is_connected.return_value = True
        
        # Configure player repository mock
        mock_repo = MagicMock()
        mock_repo._ensure_cache_loaded = AsyncMock()
        mock_get_repo.return_value = mock_repo
        
        # Import and create test client
        from main import app
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def mock_player_repository():
    """Mock PlayerRepository for testing."""
    mock_repo = Mock()
    mock_repo.get_player_by_id = AsyncMock(return_value=None)
    mock_repo.search_players = AsyncMock(return_value=[])
    mock_repo.get_all_players = AsyncMock(return_value=[])
    return mock_repo


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "player_id": "test123",
        "name": "Test Player",
        "team": "Test Team",
        "position": "P",
        "stats": {
            "batting_avg": 0.300,
            "home_runs": 25,
            "rbi": 80
        }
    }


@pytest.fixture
def mock_auth_token():
    """Mock authentication token for testing protected endpoints."""
    return "Bearer test_token_12345"


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication."""
    mock_auth = Mock()
    mock_auth.verify_id_token = Mock(return_value={
        "uid": "test_user_123",
        "email": "test@example.com"
    })
    return mock_auth
