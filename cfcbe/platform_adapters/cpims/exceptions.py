# platform_adapters/cpims/exceptions.py

"""
Custom exceptions for CPIMS adapter.
Provides specific error types for better error handling and debugging.
"""


class CPIMSAdapterError(Exception):
    """Base exception for all CPIMS adapter errors."""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "CPIMS_UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        """Convert exception to dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class CPIMSValidationError(CPIMSAdapterError):
    """Raised when input data validation fails."""

    def __init__(self, message: str, field_errors: dict = None, missing_fields: list = None):
        self.field_errors = field_errors or {}
        self.missing_fields = missing_fields or []

        details = {}
        if field_errors:
            details["field_errors"] = field_errors
        if missing_fields:
            details["missing_fields"] = missing_fields

        super().__init__(
            message=message,
            error_code="CPIMS_VALIDATION_ERROR",
            details=details
        )


class CPIMSMappingError(CPIMSAdapterError):
    """Raised when data mapping/transformation fails."""

    def __init__(self, message: str, field_name: str = None,
                 input_value: str = None, mapping_type: str = None):
        details = {
            "field_name": field_name,
            "input_value": input_value,
            "mapping_type": mapping_type
        }

        super().__init__(
            message=message,
            error_code="CPIMS_MAPPING_ERROR",
            details={k: v for k, v in details.items() if v is not None}
        )


class CPIMSGeoLookupError(CPIMSAdapterError):
    """Raised when geographic location lookup fails."""

    def __init__(self, message: str, area_name: str = None,
                 area_type: str = None, available_areas: int = None):
        details = {
            "area_name": area_name,
            "area_type": area_type,
            "available_areas": available_areas
        }

        super().__init__(
            message=message,
            error_code="CPIMS_GEO_LOOKUP_ERROR",
            details={k: v for k, v in details.items() if v is not None}
        )


class CPIMSAPIError(CPIMSAdapterError):
    """Raised when CPIMS API call fails."""

    def __init__(self, message: str, status_code: int = None,
                 response_text: str = None, endpoint: str = None,
                 is_retryable: bool = False):
        self.status_code = status_code
        self.is_retryable = is_retryable

        details = {
            "status_code": status_code,
            "endpoint": endpoint,
            "is_retryable": is_retryable
        }

        # Include truncated response text
        if response_text:
            details["response_preview"] = response_text[:200] + "..." if len(response_text) > 200 else response_text

        super().__init__(
            message=message,
            error_code="CPIMS_API_ERROR",
            details={k: v for k, v in details.items() if v is not None}
        )


class CPIMSAuthenticationError(CPIMSAPIError):
    """Raised when CPIMS authentication fails."""

    def __init__(self, message: str = "CPIMS authentication failed",
                 status_code: int = 401, response_text: str = None):
        super().__init__(
            message=message,
            status_code=status_code,
            response_text=response_text,
            endpoint=None,
            is_retryable=False
        )
        self.error_code = "CPIMS_AUTH_ERROR"


class CPIMSNetworkError(CPIMSAdapterError):
    """Raised when network communication with CPIMS fails."""

    def __init__(self, message: str, endpoint: str = None,
                 original_exception: str = None, is_timeout: bool = False):
        details = {
            "endpoint": endpoint,
            "is_timeout": is_timeout,
            "original_exception": original_exception
        }

        super().__init__(
            message=message,
            error_code="CPIMS_NETWORK_ERROR",
            details={k: v for k, v in details.items() if v is not None}
        )
        self.is_retryable = True  # Network errors are usually retryable


class CPIMSConfigurationError(CPIMSAdapterError):
    """Raised when adapter configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str = None,
                 expected_value: str = None):
        details = {
            "config_key": config_key,
            "expected_value": expected_value
        }

        super().__init__(
            message=message,
            error_code="CPIMS_CONFIG_ERROR",
            details={k: v for k, v in details.items() if v is not None}
        )


class CPIMSDataFormatError(CPIMSAdapterError):
    """Raised when input data format is invalid or unexpected."""

    def __init__(self, message: str, expected_format: str = None,
                 actual_format: str = None, field_name: str = None):
        details = {
            "expected_format": expected_format,
            "actual_format": actual_format,
            "field_name": field_name
        }

        super().__init__(
            message=message,
            error_code="CPIMS_DATA_FORMAT_ERROR",
            details={k: v for k, v in details.items() if v is not None}
        )
