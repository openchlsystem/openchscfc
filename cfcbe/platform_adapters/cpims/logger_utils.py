# platform_adapters/cpims/logger_utils.py

import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


class CPIMSLogger:
    """
    Structured logger for CPIMS adapter operations.
    Provides consistent logging format with request tracking and sanitization.
    """

    @staticmethod
    def sanitize_token(token: str, visible_chars: int = 4) -> str:
        """
        Sanitize authentication token for logging.

        Args:
            token: The token to sanitize
            visible_chars: Number of characters to show at start/end

        Returns:
            Sanitized token string
        """
        if not token:
            return "<NO_TOKEN>"
        if len(token) <= visible_chars * 2:
            return "***"
        return f"{token[:visible_chars]}...{token[-visible_chars:]}"

    @staticmethod
    def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize payload for logging by removing/masking sensitive fields.

        Args:
            payload: The payload to sanitize

        Returns:
            Sanitized copy of payload
        """
        sensitive_fields = ['token', 'password', 'secret', 'authorization', 'api_key']
        sanitized = {}

        for key, value in payload.items():
            key_lower = key.lower()
            if any(field in key_lower for field in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = CPIMSLogger.sanitize_payload(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    CPIMSLogger.sanitize_payload(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    @staticmethod
    def log_request(operation: str, case_id: str, request_id: str,
                   payload: Optional[Dict[str, Any]] = None,
                   level: str = "INFO") -> None:
        """
        Log incoming request with structured format.

        Args:
            operation: Name of the operation (e.g., "cpims_case_submission")
            case_id: Case identifier
            request_id: Unique request identifier
            payload: Optional payload to log (will be sanitized)
            level: Log level (INFO, WARNING, ERROR)
        """
        log_func = getattr(logger, level.lower())

        log_data = {
            "event": "request_received",
            "operation": operation,
            "case_id": case_id,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }

        if payload:
            log_data["payload_summary"] = {
                "has_clients": bool(payload.get("clients")),
                "has_perpetrators": bool(payload.get("perpetrators")),
                "has_narrative": bool(payload.get("narrative")),
                "category": payload.get("cat_0", "unknown")
            }

        log_func(f"📥 {operation.upper()} | {json.dumps(log_data)}")

    @staticmethod
    def log_response(operation: str, case_id: str, request_id: str,
                    status_code: int, response_data: Any,
                    duration_ms: float, level: str = "INFO") -> None:
        """
        Log response with structured format.

        Args:
            operation: Name of the operation
            case_id: Case identifier
            request_id: Unique request identifier
            status_code: HTTP status code
            response_data: Response data (will be sanitized if dict)
            duration_ms: Operation duration in milliseconds
            level: Log level
        """
        log_func = getattr(logger, level.lower())

        log_data = {
            "event": "response_sent",
            "operation": operation,
            "case_id": case_id,
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            "timestamp": datetime.now().isoformat()
        }

        if isinstance(response_data, dict):
            log_data["response_summary"] = {
                "status": response_data.get("status", "unknown"),
                "has_cpims_response": "cpims_response" in response_data
            }

        log_func(f"📤 {operation.upper()} | {json.dumps(log_data)}")

    @staticmethod
    def log_error(operation: str, case_id: str, request_id: str,
                 error_type: str, error_message: str,
                 error_details: Optional[Dict[str, Any]] = None,
                 exc_info: bool = False) -> None:
        """
        Log error with structured format and full context.

        Args:
            operation: Name of the operation
            case_id: Case identifier
            request_id: Unique request identifier
            error_type: Type of error (e.g., "validation_error", "network_error")
            error_message: Human-readable error message
            error_details: Additional error context
            exc_info: Whether to include exception traceback
        """
        log_data = {
            "event": "error_occurred",
            "operation": operation,
            "case_id": case_id,
            "request_id": request_id,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }

        if error_details:
            log_data["error_details"] = CPIMSLogger.sanitize_payload(error_details)

        logger.error(f"❌ {operation.upper()} ERROR | {json.dumps(log_data)}",
                    exc_info=exc_info)

    @staticmethod
    def log_validation_error(operation: str, case_id: str, request_id: str,
                           field_errors: Dict[str, str]) -> None:
        """
        Log validation errors with field-level details.

        Args:
            operation: Name of the operation
            case_id: Case identifier
            request_id: Unique request identifier
            field_errors: Dictionary of field names to error messages
        """
        log_data = {
            "event": "validation_failed",
            "operation": operation,
            "case_id": case_id,
            "request_id": request_id,
            "field_errors": field_errors,
            "error_count": len(field_errors),
            "timestamp": datetime.now().isoformat()
        }

        logger.warning(f"⚠️ {operation.upper()} VALIDATION | {json.dumps(log_data)}")

    @staticmethod
    def log_external_api_call(operation: str, url: str, method: str,
                            request_id: str, status_code: Optional[int] = None,
                            duration_ms: Optional[float] = None,
                            error: Optional[str] = None) -> None:
        """
        Log external API call (e.g., to CPIMS or geo endpoint).

        Args:
            operation: Name of the operation
            url: API endpoint URL
            method: HTTP method
            request_id: Unique request identifier
            status_code: Response status code (if completed)
            duration_ms: Call duration in milliseconds
            error: Error message if call failed
        """
        log_data = {
            "event": "external_api_call",
            "operation": operation,
            "url": url,
            "method": method,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }

        if status_code:
            log_data["status_code"] = status_code
        if duration_ms:
            log_data["duration_ms"] = round(duration_ms, 2)
        if error:
            log_data["error"] = error

        level = "error" if error or (status_code and status_code >= 400) else "info"
        log_func = getattr(logger, level)

        icon = "🌐" if not error else "💥"
        log_func(f"{icon} EXTERNAL_API | {json.dumps(log_data)}")

    @staticmethod
    def log_data_transformation(operation: str, request_id: str,
                               transformation_type: str,
                               input_summary: Dict[str, Any],
                               output_summary: Dict[str, Any]) -> None:
        """
        Log data transformation steps for debugging.

        Args:
            operation: Name of the operation
            request_id: Unique request identifier
            transformation_type: Type of transformation (e.g., "location_mapping", "category_lookup")
            input_summary: Summary of input data
            output_summary: Summary of output data
        """
        log_data = {
            "event": "data_transformation",
            "operation": operation,
            "request_id": request_id,
            "transformation_type": transformation_type,
            "input": input_summary,
            "output": output_summary,
            "timestamp": datetime.now().isoformat()
        }

        logger.debug(f"🔄 TRANSFORM | {json.dumps(log_data)}")


def track_cpims_operation(operation_name: str):
    """
    Decorator to track CPIMS operations with automatic logging and timing.

    Args:
        operation_name: Name of the operation for logging

    Example:
        @track_cpims_operation("send_to_cpims")
        def _send_to_cpims(self, helpline_data):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = datetime.now()

            # Try to extract case_id from args
            case_id = "unknown"
            if len(args) > 1 and isinstance(args[1], dict):
                case_id = args[1].get("id", "unknown")

            try:
                logger.info(f"🚀 Starting {operation_name} | request_id={request_id} | case_id={case_id}")
                result = func(*args, **kwargs)

                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                logger.info(f"✅ Completed {operation_name} | request_id={request_id} | duration={duration_ms:.2f}ms")

                return result

            except Exception as e:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                CPIMSLogger.log_error(
                    operation=operation_name,
                    case_id=case_id,
                    request_id=request_id,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_details={"duration_ms": duration_ms},
                    exc_info=True
                )
                raise

        return wrapper
    return decorator
