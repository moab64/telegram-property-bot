import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Optional

class CustomFormatter(logging.Formatter):
    """Custom formatter for colored and structured logs"""
    
    # Color codes
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    # Format string
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Level-specific formats
    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: GREEN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class FileFormatter(logging.Formatter):
    """Formatter for file logs"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
):
    """
    Setup logging configuration
    
    Args:
        level: Logging level
        log_file: Path to log file (if None, only console logging)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(FileFormatter())
        logger.addHandler(file_handler)
    
    # Set levels for specific loggers
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get logger with given name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_execution_time(logger: logging.Logger):
    """
    Decorator to log function execution time
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {func.__name__} failed after {execution_time:.2f} seconds: {e}")
                raise
        
        def sync_wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {func.__name__} failed after {execution_time:.2f} seconds: {e}")
                raise
        
        if func.__name__.startswith('async_') or func.__name__ in ['crawl', 'send_ads_to_users']:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class BotLogger:
    """Custom logger for bot-specific events"""
    
    def __init__(self, name: str = "bot"):
        self.logger = get_logger(name)
    
    def user_started(self, user_id: int, username: str, first_name: str):
        """Log when user starts the bot"""
        self.logger.info(f"User started: ID={user_id}, Username=@{username}, Name={first_name}")
    
    def filter_updated(self, user_id: int, filter_data: dict):
        """Log when user updates filters"""
        self.logger.info(f"Filter updated: User={user_id}, Data={filter_data}")
    
    def ad_sent(self, user_id: int, ad_id: int, ad_title: str):
        """Log when ad is sent to user"""
        self.logger.info(f"Ad sent: User={user_id}, AdID={ad_id}, Title={ad_title[:50]}...")
    
    def crawler_started(self, source: str, city: str, property_type: str):
        """Log when crawler starts"""
        self.logger.info(f"Crawler started: Source={source}, City={city}, Type={property_type}")
    
    def crawler_finished(self, source: str, ads_found: int, new_ads: int):
        """Log when crawler finishes"""
        self.logger.info(f"Crawler finished: Source={source}, Found={ads_found}, New={new_ads}")
    
    def error(self, event: str, error: Exception, user_id: int = None):
        """Log error with context"""
        context = f"User={user_id}, " if user_id else ""
        self.logger.error(f"Error in {event}: {context}Error={str(error)}")
    
    def warning(self, event: str, message: str, user_id: int = None):
        """Log warning with context"""
        context = f"User={user_id}, " if user_id else ""
        self.logger.warning(f"Warning in {event}: {context}Message={message}")

def setup_bot_logging():
    """Setup logging for the bot application"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Main log file
    log_file = logs_dir / "bot.log"
    
    # Setup logging
    setup_logging(
        level=logging.INFO,
        log_file=str(log_file),
        max_bytes=10 * 1024 * 1024,  # 10 MB
        backup_count=5
    )
    
    # Create separate log files for different components
    components = ['crawler', 'database', 'scheduler']
    for component in components:
        component_log_file = logs_dir / f"{component}.log"
        component_logger = logging.getLogger(component)
        
        # Remove existing handlers
        for handler in component_logger.handlers[:]:
            component_logger.removeHandler(handler)
        
        # Add file handler
        file_handler = logging.handlers.RotatingFileHandler(
            component_log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(FileFormatter())
        component_logger.addHandler(file_handler)
    
    logging.info("Logging setup completed")

# Initialize logging when module is imported
setup_bot_logging()