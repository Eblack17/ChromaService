import logging
import logging.handlers
import json
import sys
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from functools import wraps
import traceback
from .config import get_settings

settings = get_settings()

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.extras = kwargs
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
            **self.extras
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
            
        # Add custom fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
            
        # Add context from LoggerAdapter
        if hasattr(record, "context"):
            log_data.update(record.context)
            
        return json.dumps(log_data)

class StandardFormatter(logging.Formatter):
    """Standard formatter for human-readable logs."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(context)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with context.
        
        Args:
            record: Log record to format
            
        Returns:
            str: Formatted log message
        """
        # Add context string if present
        if hasattr(record, "context"):
            context = record.context
            if isinstance(context, dict):
                context_str = " ".join(f"{k}={v}" for k, v in context.items())
                if context_str:
                    record.context = f"[{context_str}] "
                else:
                    record.context = ""
            else:
                record.context = str(context)
        else:
            record.context = ""
            
        return super().format(record)

def setup_logging(
    app_name: str = settings.APP_NAME,
    log_level: str = settings.LOG_LEVEL,
    log_format: str = settings.LOG_FORMAT
) -> None:
    """Set up application logging configuration.
    
    Args:
        app_name: Name of the application
        log_level: Logging level (DEBUG, INFO, etc.)
        log_format: Log format (standard or json)
    """
    # Convert string log level to constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    json_formatter = JSONFormatter(app_name=app_name, environment=settings.APP_ENV)
    standard_formatter = StandardFormatter()
    formatter = json_formatter if log_format == "json" else standard_formatter
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handlers
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f"{app_name.lower().replace(' ', '_')}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / f"{app_name.lower().replace(' ', '_')}_error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context to logs."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process log message with context.
        
        Args:
            msg: Log message
            kwargs: Additional arguments
            
        Returns:
            tuple: Processed message and kwargs
        """
        # Ensure extra dict exists
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        # Add context to extra
        kwargs["extra"]["context"] = self.extra
        
        return msg, kwargs

def get_logger(name: str, **kwargs) -> LoggerAdapter:
    """Get a logger with context.
    
    Args:
        name: Logger name
        **kwargs: Additional context
        
    Returns:
        LoggerAdapter: Configured logger
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, kwargs)

def log_execution_time(logger: Optional[logging.Logger] = None):
    """Decorator to log function execution time.
    
    Args:
        logger: Logger to use (if None, creates a new one)
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
            
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"Function '{func.__name__}' executed in {execution_time:.2f} seconds",
                    extra={"execution_time": execution_time}
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Function '{func.__name__}' failed after {execution_time:.2f} seconds",
                    exc_info=True,
                    extra={
                        "execution_time": execution_time,
                        "error_type": type(e).__name__
                    }
                )
                raise
        return wrapper
    return decorator

def monitor_api_call(logger: Optional[logging.Logger] = None):
    """Decorator to monitor API calls.
    
    Args:
        logger: Logger to use (if None, creates a new one)
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
            
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"API call to '{func.__name__}' successful",
                    extra={
                        "api_call": func.__name__,
                        "execution_time": execution_time,
                        "status": "success"
                    }
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"API call to '{func.__name__}' failed",
                    exc_info=True,
                    extra={
                        "api_call": func.__name__,
                        "execution_time": execution_time,
                        "status": "error",
                        "error_type": type(e).__name__
                    }
                )
                raise
        return wrapper
    return decorator

# Initialize logging when module is imported
setup_logging() 
