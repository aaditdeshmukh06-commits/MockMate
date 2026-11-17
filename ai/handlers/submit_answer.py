"""
MockMate - Submit Answer Lambda Handler
POST /interview/answer
Evaluates answer, stores QA, returns next question or completion status.
"""

import json
import time
from typing import Any, Dict

from shared.utils import (
    cors_response,
    parse_body,
    get_user_id_from_event,
    bad_request,
    not_found,
    unauthorized,
)
from shared.database import get_session, update_session
from shared.questions import get_question
from shared.evaluation import evaluate_answer


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle POST /interview/answer

    Request body:
    {
        "sessionId": "string",
        "answer": "string",
        "questionNumber": 1,
        "bodyLanguageMetrics?": {...}
    }

    Response:
    {
        "nextQuestion": "string|null",
        "questionNumber": 2,
        "totalQuestions": 5,
        "isComplete": false,
        "evaluation": {...}
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
    required_fields = ["sessionId", "answer", "questionNumber"]
    for field in required_fields:
        if field not in body:
            return bad_request(f"Missing required field: {field}")

    session_id = body["sessionId"]
    answer = body["answer"]
    question_number = body["questionNumber"]
    body_language_metrics = body.get("bodyLanguageMetrics")

    # Retrieve session
    session = get_session(session_id)
    if not session:
        return not_found("Session not found")

    # Verify ownership
    if session.get("userId") != user_id:
        return unauthorized("Session does not belong to user")

    # Verify session is active
    if session.get("status") != "in_progress":
        return bad_request("Interview already completed")

    # Verify question number matches
    if session.get("currentQuestion") != question_number:
        return bad_request(f"Question number mismatch. Expected {session.get('currentQuestion')}, got {question_number}")

    # Evaluate answer
    evaluation = evaluate_answer(answer, question_number)

    # Build QA item
    qa_item = {
        "questionNumber": question_number,
        "question": session.get("currentQuestionText"),
        "answer": answer,
        "evaluation": evaluation,
        "bodyLanguageMetrics": body_language_metrics,
        "timestamp": int(time.time() * 1000),
    }

    # Update session with new QA item
    qa_history = session.get("qaHistory", [])
    qa_history.append(qa_item)

    body_language_list = session.get("bodyLanguageMetrics", [])
    if body_language_metrics:
        body_language_list.append(body_language_metrics)

    next_question_number = question_number + 1
    is_complete = next_question_number > session.get("totalQuestions", 5)

    updates = {
        "qaHistory": qa_history,
        "bodyLanguageMetrics": body_language_list,
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    if is_complete:
        updates["status"] = "completed"
        updates["currentQuestion"] = next_question_number
        next_question = None
    else:
        next_question = get_question(
            session["role"],
            session["difficulty"],
            next_question_number
        )
        updates["currentQuestion"] = next_question_number
        updates["currentQuestionText"] = next_question

    try:
        update_session(session_id, updates)
    except Exception as e:
        print(f"DynamoDB error: {e}")
        return cors_response(500, {
            "message": "Failed to update session",
            "code": "DATABASE_ERROR",
            "status": 500,
        })

    # Return response
    return cors_response(200, {
        "nextQuestion": next_question,
        "questionNumber": next_question_number,
        "totalQuestions": session.get("totalQuestions", 5),
        "isComplete": is_complete,
        "evaluation": evaluation,
    })


# For local testing
if __name__ == "__main__":
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "sessionId": "sess_test123",
            "answer": "I have experience with Python and JavaScript. I built a web application using React and Django.",
            "questionNumber": 1,
        }),
        "requestContext": {
            "authorizer": {
                "claims": {"sub": "test-user-123"}
            }
        }
    }
    # This would fail without a real session in DynamoDB
    # result = lambda_handler(test_event, None)
    # print(json.dumps(result, indent=2))
    print("Local test requires DynamoDB session. Use local_test.py instead.")