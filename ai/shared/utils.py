"""
MockMate - Common Utilities
CORS headers, error responses, and shared helpers
"""

import json
import os
from typing import Any, Dict, Optional

from .db_utils import decimal_default


# CORS headers for API Gateway responses
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json",
}


def cors_response(status_code: int, body: Any) -> Dict[str, Any]:
    """
    Create a standard API Gateway response with CORS headers.
    Automatically handles Decimal conversion for JSON serialization.
    """
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, default=decimal_default),
    }


def success_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create a successful response with CORS headers."""
    return cors_response(status_code, data)


def error_response(message: str, code: str = "INTERNAL_ERROR", status_code: int = 500) -> Dict[str, Any]:
    """Create an error response with CORS headers."""
    return cors_response(status_code, {
        "message": message,
        "code": code,
        "status": status_code,
    })


def bad_request(message: str) -> Dict[str, Any]:
    """Create a 400 Bad Request response."""
    return error_response(message, "BAD_REQUEST", 400)


def not_found(message: str = "Resource not found") -> Dict[str, Any]:
    """Create a 404 Not Found response."""
    return error_response(message, "NOT_FOUND", 404)


def unauthorized(message: str = "Unauthorized") -> Dict[str, Any]:
    """Create a 401 Unauthorized response."""
    return error_response(message, "UNAUTHORIZED", 401)


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse JSON body from API Gateway event."""
    body = event.get("body")
    if not body:
        return {}
    if isinstance(body, str):
        return json.loads(body)
    return body


def get_user_id_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    Extract userId from Cognito authorizer context.
    Supports both HTTP API JWT authorizer and REST API authorizer shapes.
    """
    # HTTP API JWT authorizer
    try:
        return event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    except (KeyError, TypeError, AttributeError):
        pass
    # REST API authorizer
    try:
        return event["requestContext"]["authorizer"]["claims"]["sub"]
    except (KeyError, TypeError, AttributeError):
        return None


def get_query_param(event: Dict[str, Any], param: str, default: Any = None) -> Any:
    """Safely get query string parameter from event."""
    params = event.get("queryStringParameters") or {}
    return params.get(param, default)


def get_env(key: str, default: Any = None) -> Any:
    """Get environment variable with optional default."""
    return os.environ.get(key, default)


def is_mock_mode() -> bool:
    """Check if mock mode is enabled via USE_MOCK env var."""
    return get_env("USE_MOCK", "false").lower() == "true"


def get_table_name() -> str:
    """Get DynamoDB table name from environment."""
    return get_env("TABLE_NAME", "MockMateInterviews")


def get_region() -> str:
    """Get AWS region from environment."""
    return get_env("REGION", "us-east-1")