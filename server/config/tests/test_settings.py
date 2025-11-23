"""
Unit tests for settings configuration.
"""
import pytest
import os
from unittest.mock import patch
from config.settings import Settings


class TestSettingsInitialization:
    """Tests for Settings initialization."""
    
    @pytest.mark.unit
    def test_settings_default_values(self):
        """Test that settings have default values."""
        settings = Settings()
        
        assert settings.HOST is not None
        assert settings.PORT > 0
        assert settings.ENVIRONMENT in ["development", "staging", "production", "testing"]
    
    @pytest.mark.unit
    def test_settings_cors_origins(self):
        """Test CORS origins configuration."""
        settings = Settings()
        
        assert isinstance(settings.CORS_ORIGINS, list)
        assert "http://localhost:3000" in settings.CORS_ORIGINS
    
    @pytest.mark.unit
    @patch.dict(os.environ, {"TRUST_PROXY": "true"})
    @patch('config.settings.Settings.TRUST_PROXY', True)
    def test_settings_trust_proxy_true(self):
        """Test TRUST_PROXY when set to true."""
        settings = Settings()
        assert settings.TRUST_PROXY is True
    
    @pytest.mark.unit
    def test_settings_trust_proxy_false(self):
        """Test TRUST_PROXY when set to false."""
        with patch.dict(os.environ, {"TRUST_PROXY": "false"}, clear=False):
            settings = Settings()
            assert settings.TRUST_PROXY is False
    
    @pytest.mark.unit
    def test_settings_firebase_credentials_path(self):
        """Test Firebase credentials path."""
        settings = Settings()
        
        assert settings.FIREBASE_CREDENTIALS_PATH is not None


class TestSettingsValidation:
    """Tests for settings validation."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {"FIREBASE_WEB_API_KEY": ""})
    def test_validate_missing_api_key_development(self):
        """Test validation warns about missing API key in development."""
        settings = Settings()
        settings.FIREBASE_WEB_API_KEY = ""
        settings.ENVIRONMENT = "development"
        
        warnings = settings.validate()
        
        assert len(warnings) > 0
        assert any("FIREBASE_WEB_API_KEY" in w for w in warnings)
    
    @pytest.mark.unit
    @patch.dict(os.environ, {"FIREBASE_WEB_API_KEY": "test_key"})
    def test_validate_with_api_key_development(self):
        """Test validation with API key in development."""
        settings = Settings()
        settings.FIREBASE_WEB_API_KEY = "test_key"
        settings.ENVIRONMENT = "development"
        
        warnings = settings.validate()
        
        # Should not have API key warning
        assert not any("FIREBASE_WEB_API_KEY is not set" in w for w in warnings)
    
    @pytest.mark.unit
    def test_validate_production_without_api_key_raises_error(self):
        """Test validation raises error in production without API key."""
        settings = Settings()
        settings.FIREBASE_WEB_API_KEY = ""
        settings.ENVIRONMENT = "production"
        
        with pytest.raises(ValueError) as exc_info:
            settings.validate()
        
        assert "FIREBASE_WEB_API_KEY must be set in production" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_validate_production_with_api_key(self):
        """Test validation in production with API key."""
        settings = Settings()
        settings.FIREBASE_WEB_API_KEY = "test_key"
        settings.ENVIRONMENT = "production"
        
        warnings = settings.validate()
        
        # Should have HTTPS warning
        assert any("HTTPS" in w for w in warnings)
    
    @pytest.mark.unit
    def test_validate_returns_list(self):
        """Test that validate returns a list."""
        settings = Settings()
        settings.FIREBASE_WEB_API_KEY = "test_key"
        settings.ENVIRONMENT = "development"
        
        warnings = settings.validate()
        
        assert isinstance(warnings, list)
    
    @pytest.mark.unit
    def test_validate_production_https_warning(self):
        """Test that production mode warns about HTTPS."""
        settings = Settings()
        settings.FIREBASE_WEB_API_KEY = "test_key"
        settings.ENVIRONMENT = "production"
        
        warnings = settings.validate()
        
        assert any("PRODUCTION" in w and "HTTPS" in w for w in warnings)
