"""
Custom exceptions for better error handling and debugging
"""


class BotError(Exception):
    """Base exception for all bot errors"""
    
    def __init__(self, message: str, error_code: str = None, context: dict = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context
        }


class ConfigurationError(BotError):
    """Configuration-related errors"""
    
    def __init__(self, message: str, missing_field: str = None):
        context = {"missing_field": missing_field} if missing_field else {}
        super().__init__(message, "CONFIG_ERROR", context)


class TelegramConnectionError(BotError):
    """Telegram connection errors"""
    
    def __init__(self, message: str, retry_after: int = None):
        context = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, "TELEGRAM_CONNECTION_ERROR", context)


class RateLimitError(BotError):
    """Rate limiting errors"""
    
    def __init__(self, message: str, retry_after: int, limit_type: str = "telegram"):
        context = {
            "retry_after": retry_after,
            "limit_type": limit_type
        }
        super().__init__(message, "RATE_LIMIT_ERROR", context)


class MessageProcessingError(BotError):
    """Message processing errors"""
    
    def __init__(self, message: str, message_id: str = None, source: str = None):
        context = {
            "message_id": message_id,
            "source": source
        }
        super().__init__(message, "MESSAGE_PROCESSING_ERROR", context)


class FilterError(BotError):
    """Message filtering errors"""
    
    def __init__(self, message: str, filter_type: str = None, reason: str = None):
        context = {
            "filter_type": filter_type,
            "reason": reason
        }
        super().__init__(message, "FILTER_ERROR", context)


class StorageError(BotError):
    """Database/storage errors"""
    
    def __init__(self, message: str, operation: str = None, table: str = None):
        context = {
            "operation": operation,
            "table": table
        }
        super().__init__(message, "STORAGE_ERROR", context)


class AIServiceError(BotError):
    """AI service errors"""
    
    def __init__(self, message: str, service: str = "groq", retry_count: int = 0):
        context = {
            "service": service,
            "retry_count": retry_count
        }
        super().__init__(message, "AI_SERVICE_ERROR", context)


class ChannelAccessError(BotError):
    """Channel access errors"""
    
    def __init__(self, message: str, channel: str = None, required_permission: str = None):
        context = {
            "channel": channel,
            "required_permission": required_permission
        }
        super().__init__(message, "CHANNEL_ACCESS_ERROR", context)


class ValidationError(BotError):
    """Input validation errors"""
    
    def __init__(self, message: str, field: str = None, value: any = None):
        context = {
            "field": field,
            "value": str(value) if value else None
        }
        super().__init__(message, "VALIDATION_ERROR", context)


# Error code constants
class ErrorCodes:
    """Error code constants for categorization"""
    
    # Configuration
    CONFIG_MISSING = "CONFIG_001"
    CONFIG_INVALID = "CONFIG_002"
    
    # Telegram
    TELEGRAM_AUTH_FAILED = "TELEGRAM_001"
    TELEGRAM_FLOOD_WAIT = "TELEGRAM_002"
    TELEGRAM_NETWORK = "TELEGRAM_003"
    TELEGRAM_CHANNEL_ACCESS = "TELEGRAM_004"
    
    # Processing
    PROCESSING_FAILED = "PROCESS_001"
    PROCESSING_TIMEOUT = "PROCESS_002"
    
    # Storage
    STORAGE_WRITE_FAILED = "STORAGE_001"
    STORAGE_READ_FAILED = "STORAGE_002"
    STORAGE_LOCKED = "STORAGE_003"
    
    # AI
    AI_REQUEST_FAILED = "AI_001"
    AI_QUOTA_EXCEEDED = "AI_002"
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_001"
    DAILY_LIMIT_REACHED = "RATE_002"


def format_error_message(error: Exception, include_traceback: bool = False) -> str:
    """
    Format error message for logging
    
    Args:
        error: Exception instance
        include_traceback: Whether to include traceback
    
    Returns:
        Formatted error message
    """
    if isinstance(error, BotError):
        msg = f"[{error.error_code}] {error.message}"
        if error.context:
            msg += f" | Context: {error.context}"
        return msg
    else:
        return f"[UNEXPECTED] {type(error).__name__}: {str(error)}"
