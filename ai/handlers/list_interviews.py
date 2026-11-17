"""
MockMate - List Interviews Lambda Handler
GET /interviews?userId=
Returns interview history for a user.
"""

from typing import Any

from shared.database import get_user_interviews
from shared.utils import (
    cors_response,
    get_query_param,
    get_user_id_from_event,
    unauthorized,
)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Handle GET /interviews?userId=

    Query parameters:
    - userId: string (required)

    Response:
    {
        "interviews": [
            {
                "sessionId": "string",
                "role": "string",
                "difficulty": "string",
                "overallScore": number,
                "categoryScores": {technical, communication, confidence, problemSolving, bodyLanguage},
                "date": "ISO timestamp",
                "durationMinutes": number,
                "status": "completed"
            }
        ]
    }
    Sorted newest first by date.
    """
    # Handle OPTIONS preflight
    if event.get("httpMethod") == "OPTIONS":
        return cors_response(204, {})

    # Get user ID from Cognito authorizer
    auth_user_id = get_user_id_from_event(event)
    if not auth_user_id:
        return unauthorized("User not authenticated")

    # Get userId from query params (allow override for admin, but verify auth)
    query_user_id = get_query_param(event, "userId")

    # Use authenticated user's ID if not provided, otherwise verify match
    if query_user_id:
        if query_user_id != auth_user_id:
            return unauthorized("Cannot access other user's interviews")
        user_id = query_user_id
    else:
        user_id = auth_user_id

    try:
        interviews = get_user_interviews(user_id)
    except Exception as e:
        print(f"DynamoDB error: {e}")
        return cors_response(500, {
            "message": "Failed to retrieve interviews",
            "code": "DATABASE_ERROR",
            "status": 500,
        })

    # Format response
    # Include items that are either completed sessions (status == "completed")
    # OR report rows (have overallScore field, meaning report was generated)
    formatted = []
    for interview in interviews:
        # Check if this is a completed interview:
        # - Session with status "completed", OR
        # - Report row (has overallScore, which only exists on generated reports)
        is_completed = (
            interview.get("status") == "completed"
            or interview.get("overallScore") is not None
        )

        if is_completed:
            formatted.append({
                "sessionId": interview.get("sessionId"),
                "role": interview.get("role"),
                "difficulty": interview.get("difficulty"),
                "overallScore": interview.get("overallScore", 0),
                "categoryScores": interview.get("categoryScores", {}),
                "date": interview.get("date") or interview.get("createdAt"),
                "durationMinutes": interview.get("durationMinutes", 0),
                "status": "completed",
            })

    # Sort newest first by date (get_user_interviews already returns newest first via ScanIndexForward=False,
    # but we sort again for safety in case of mixed session/report items)
    formatted.sort(key=lambda x: x.get("date", ""), reverse=True)

    return cors_response(200, {"interviews": formatted})


# For local testing
if __name__ == "__main__":
    test_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"userId": "test-user-123"},
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-123"}
            }
        }
    }
    # result = lambda_handler(test_event, None)
    # print(json.dumps(result, indent=2))
    print("Local test requires DynamoDB. Use local_test.py instead.")