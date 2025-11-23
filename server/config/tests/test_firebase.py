"""
Unit tests for Firebase service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from config.firebase import FirebaseService


class TestFirebaseServiceInitialization:
    """Tests for FirebaseService initialization."""
    
    @pytest.mark.unit
    @patch('config.firebase.firebase_admin')
    @patch('config.firebase.credentials')
    @patch('config.firebase.firestore')
    def test_firebase_service_initialization_success(self, mock_firestore, mock_credentials, mock_firebase_admin):
        """Test successful Firebase initialization."""
        mock_firebase_admin._apps = {}
        mock_credentials.Certificate.return_value = Mock()
        mock_firestore.client.return_value = Mock()
        
        service = FirebaseService()
        
        assert service.db is not None
        assert service.auth is not None
    
    @pytest.mark.unit
    @patch('config.firebase.firebase_admin')
    @patch('config.firebase.credentials')
    @patch('config.firebase.firestore')
    def test_firebase_service_already_initialized(self, mock_firestore, mock_credentials, mock_firebase_admin):
        """Test Firebase when already initialized."""
        mock_firebase_admin._apps = {"default": Mock()}
        mock_firestore.client.return_value = Mock()
        
        service = FirebaseService()
        
        # Should not call initialize_app again
        mock_firebase_admin.initialize_app.assert_not_called()
        assert service.db is not None
    
    @pytest.mark.unit
    @patch('config.firebase.firebase_admin')
    @patch('config.firebase.credentials')
    @patch('config.firebase.firestore')
    @patch('builtins.print')
    def test_firebase_service_initialization_failure(self, mock_print, mock_firestore, mock_credentials, mock_firebase_admin):
        """Test Firebase initialization failure."""
        mock_firebase_admin._apps = {}
        mock_credentials.Certificate.side_effect = Exception("Credentials error")
        
        service = FirebaseService()
        
        assert service.db is None
        mock_print.assert_called()
    
    @pytest.mark.unit
    @patch('config.firebase.firebase_admin')
    @patch('config.firebase.credentials')
    @patch('config.firebase.firestore')
    def test_is_connected_true(self, mock_firestore, mock_credentials, mock_firebase_admin):
        """Test is_connected returns True when db is set."""
        mock_firebase_admin._apps = {}
        mock_credentials.Certificate.return_value = Mock()
        mock_firestore.client.return_value = Mock()
        
        service = FirebaseService()
        
        assert service.is_connected() is True
    
    @pytest.mark.unit
    def test_is_connected_false(self):
        """Test is_connected returns False when db is None."""
        service = FirebaseService.__new__(FirebaseService)
        service.db = None
        service.auth = Mock()
        
        assert service.is_connected() is False
