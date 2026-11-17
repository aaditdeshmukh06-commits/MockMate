"""
MockMate - Save Report Lambda Handler
POST /interview/report/save
No-op endpoint for compatibility (reports are auto-saved on generation).
"""

from typing import Any, Dict

from shared.utils import cors_response, parse_body, get_user_id_from_event, unauthorized


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle POST /interview/report/save

    Request body:
    {
        "report": {...}
    }

    Response:
    {
        "success": true
    }
    """
    # Handle OPTIONS preflight
    if event.get("httpMethod") == "OPTIONS":
        return cors_response(204, {})

    # Get user ID from Cognito authorizer
    user_id = get_user_id_from_event(event)
    if not user_id:
        return unauthorized("User not authenticated")

    # Parse request body (no-op, just acknowledge)
    try:
        parse_body(event)
    except Exception:
        pass  # Ignore parse errors for no-op

    return cors_response(200, {"success": True})


# For local testing
if __name__ == "__main__":
    test_event = {
        "httpMethod": "POST",
        "body": '{"report": {}}',
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-123"}
            }
        }
    }
    result = lambda_handler(test_event, None)
    import json
    print(json.dumps(result, indent=2))