"""
MockMate - Get Report Lambda Handler
POST /interview/report
Generates final interview report from session data.
"""

import json
from typing import Any, Dict

from shared.utils import (
    cors_response,
    parse_body,
    get_user_id_from_event,
    bad_request,
    not_found,
    unauthorized,
)
from shared.database import get_session, put_report
from shared.reporting import generate_report


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle POST /interview/report

    Request body:
    {
        "sessionId": "string",
        "userId": "string",
        "qaHistory": [...],
        "bodyLanguageMetrics": [...]
    }

    Response:
    {
        "report": {...}
    }
    """
    # Handle OPTIONS preflight
    if event.get("httpMethod") == "OPTIONS":
        return cors_response(204, {})

    # Get user ID from Cognito authorizer
    user_id = get_user_id_from_event(event)
    if not user_id:
        return unauthorized("User not authenticated")

    # Parse request body
    try:
        body = parse_body(event)
    except json.JSONDecodeError:
        return bad_request("Invalid JSON body")

    # Validate required fields
    required_fields = ["sessionId", "userId", "qaHistory", "bodyLanguageMetrics"]
    for field in required_fields:
        if field not in body:
            return bad_request(f"Missing required field: {field}")

    session_id = body["sessionId"]
    request_user_id = body["userId"]
    qa_history = body["qaHistory"]
    body_language_metrics = body["bodyLanguageMetrics"]

    # Verify userId matches authenticated user
    if request_user_id != user_id:
        return unauthorized("User ID mismatch")

    # Retrieve session for role/difficulty/startTime
    session = get_session(session_id)
    if not session:
        return not_found("Session not found")

    # Verify ownership
    if session.get("userId") != user_id:
        return unauthorized("Session does not belong to user")

    # Generate report
    try:
        report = generate_report(
            session_id=session_id,
            user_id=user_id,
            role=session["role"],
            difficulty=session["difficulty"],
            qa_history=qa_history,
            body_language_metrics=body_language_metrics,
            start_time=session.get("startTime"),
        )
    except Exception as e:
        print(f"Report generation error: {e}")
        return cors_response(500, {
            "message": "Failed to generate report",
            "code": "REPORT_GENERATION_ERROR",
            "status": 500,
        })

    # Store report in DynamoDB
    try:
        put_report(report)
    except Exception as e:
        print(f"DynamoDB error storing report: {e}")
        return cors_response(500, {
            "message": "Failed to save report",
            "code": "DATABASE_ERROR",
            "status": 500,
        })

    # Return response
    return cors_response(200, {"report": report})


# For local testing
if __name__ == "__main__":
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "sessionId": "sess_test123",
            "userId": "test-user-123",
            "qaHistory": [],
            "bodyLanguageMetrics": [],
        }),
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-123"}
            }
        }
    }
    # result = lambda_handler(test_event, None)
    # print(json.dumps(result, indent=2))
    print("Local test requires DynamoDB session. Use local_test.py instead.")