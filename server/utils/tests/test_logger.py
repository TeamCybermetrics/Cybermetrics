"""
Unit tests for logger utility functions.
"""
import pytest
import logging
from utils.logger import setup_logger, get_logger


class TestLogger:
    """Tests for logger utility functions."""
    
    @pytest.mark.unit
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger with the correct name."""
        logger_name = "test_logger"
        logger = setup_logger(logger_name)
        
        assert logger is not None
        assert logger.name == logger_name
        assert isinstance(logger, logging.Logger)
    
    @pytest.mark.unit
    def test_setup_logger_sets_info_level(self):
        """Test that logger is configured with INFO level."""
        logger = setup_logger("test_info_level")
        assert logger.level == logging.INFO
    
    @pytest.mark.unit
    def test_setup_logger_adds_handler(self):
        """Test that logger has at least one handler."""
        logger = setup_logger("test_handler")
        assert len(logger.handlers) > 0
    
    @pytest.mark.unit
    def test_setup_logger_idempotent(self):
        """Test that calling setup_logger multiple times doesn't add duplicate handlers."""
        logger_name = "test_idempotent"
        logger1 = setup_logger(logger_name)
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger(logger_name)
        assert len(logger2.handlers) == initial_handler_count
        assert logger1 is logger2
    
    @pytest.mark.unit
    def test_get_logger_alias(self):
        """Test that get_logger is an alias for setup_logger."""
        logger_name = "test_alias"
        logger1 = setup_logger(logger_name)
        logger2 = get_logger(logger_name)
        
        assert logger1 is logger2
    
    @pytest.mark.unit
    def test_logger_has_formatter(self):
        """Test that logger handler has a formatter configured."""
        logger = setup_logger("test_formatter")
        handler = logger.handlers[0]
        
        assert handler.formatter is not None
        assert "%(asctime)s" in handler.formatter._fmt
        assert "%(name)s" in handler.formatter._fmt
        assert "%(levelname)s" in handler.formatter._fmt
        assert "%(message)s" in handler.formatter._fmt
