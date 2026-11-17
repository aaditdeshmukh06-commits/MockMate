"""
MockMate - Start Interview Lambda Handler
POST /interview/start
Creates a new interview session and returns the first question.
"""

import json
import time
import uuid
from typing import Any, Dict

from shared.utils import (
    cors_response,
    parse_body,
    get_user_id_from_event,
    bad_request,
    unauthorized,
)
from shared.database import put_session
from shared.questions import get_question, get_total_questions


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle POST /interview/start

    Request body:
    {
        "userId": "string",
        "role": "string",
        "difficulty": "easy|medium|hard",
        "language": "string",
        "jdText?": "string",
        "resumeText?": "string"
    }

    Response:
    {
        "sessionId": "string",
        "firstQuestion": "string",
        "questionNumber": 1,
        "totalQuestions": 5
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
    required_fields = ["userId", "role", "difficulty", "language"]
    for field in required_fields:
        if not body.get(field):
            return bad_request(f"Missing required field: {field}")

    # Verify userId matches authenticated user
    if body["userId"] != user_id:
        return unauthorized("User ID mismatch")

    # Validate difficulty
    difficulty = body["difficulty"].lower()
    if difficulty not in ("easy", "medium", "hard"):
        return bad_request("Invalid difficulty. Must be: easy, medium, or hard")

    # Generate session ID
    session_id = f"sess_{int(time.time() * 1000)}_{uuid.uuid4().hex[:9]}"

    # Get first question
    first_question = get_question(body["role"], difficulty, 1)
    total_questions = get_total_questions()

    # Create session object
    session = {
        "sessionId": session_id,
        "userId": user_id,
        "role": body["role"],
        "difficulty": difficulty,
        "language": body["language"],
        "jdText": body.get("jdText", ""),
        "resumeText": body.get("resumeText", ""),
        "currentQuestion": 1,
        "totalQuestions": total_questions,
        "currentQuestionText": first_question,
        "qaHistory": [],
        "bodyLanguageMetrics": [],
        "startTime": int(time.time() * 1000),
        "status": "in_progress",
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # Store in DynamoDB
    try:
        put_session(session)
    except Exception as e:
        print(f"DynamoDB error: {e}")
        return cors_response(500, {
            "message": "Failed to create session",
            "code": "DATABASE_ERROR",
            "status": 500,
        })

    # Return response
    return cors_response(200, {
        "sessionId": session_id,
        "firstQuestion": first_question,
        "questionNumber": 1,
        "totalQuestions": total_questions,
    })


# For local testing
if __name__ == "__main__":
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "userId": "test-user-123",
            "role": "Software Engineer",
            "difficulty": "medium",
            "language": "English",
        }),
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-123"}
            }
        }
    }
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))