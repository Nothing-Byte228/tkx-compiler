"""Logging configuration and utilities for tkx-compiler."""
import logging
import sys
from typing import Optional
from pathlib import Path


class Logger:
    """Centralized logger for tkx-compiler."""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize logger (only once)."""
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self, log_level: str = "INFO", log_file: Optional[str] = None) -> None:
        """Setup logger with handlers and formatters.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional path to log file
        """
        self._logger = logging.getLogger("tkx_compiler")
        self._logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Console formatter
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # File formatter with more details
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
    
    def configure(self, log_level: str = "INFO", log_file: Optional[str] = None) -> None:
        """Reconfigure logger.
        
        Args:
            log_level: Logging level
            log_file: Optional path to log file
        """
        self._setup_logger(log_level, log_file)
    
    def debug(self, message: str) -> None:
        """Log debug message.
        
        Args:
            message: Message to log
        """
        self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message.
        
        Args:
            message: Message to log
        """
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message.
        
        Args:
            message: Message to log
        """
        self._logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message.
        
        Args:
            message: Message to log
            exc_info: Include exception info
        """
        self._logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """Log critical message.
        
        Args:
            message: Message to log
            exc_info: Include exception info
        """
        self._logger.critical(message, exc_info=exc_info)
    
    @classmethod
    def get_logger(cls) -> 'Logger':
        """Get logger instance.
        
        Returns:
            Logger instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Convenience functions
def get_logger() -> Logger:
    """Get logger instance.
    
    Returns:
        Logger instance
    """
    return Logger.get_logger()


def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure logging.
    
    Args:
        log_level: Logging level
        log_file: Optional path to log file
    """
    logger = get_logger()
    logger.configure(log_level, log_file)