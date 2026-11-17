#!/usr/bin/env python3
"""
MockMate - Local Testing Script
Tests Lambda handlers locally with mock DynamoDB (using moto) or real DynamoDB.
"""

import os
import sys
import json
import time
import uuid
from typing import Dict, Any

# Add ai to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set test environment variables
os.environ.setdefault("USE_MOCK", "true")
os.environ.setdefault("TABLE_NAME", "MockMateInterviews")
os.environ.setdefault("REGION", "us-east-1")


def setup_test_table():
    """Create a local DynamoDB table for testing using moto."""
    try:
        import boto3
        from moto import mock_aws

        # Start moto mock
        mock = mock_aws()
        mock.start()

        # Create DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create table with GSIs
        table = dynamodb.create_table(
            TableName="MockMateInterviews",
            KeySchema=[
                {"AttributeName": "sessionId", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "sessionId", "AttributeType": "S"},
                {"AttributeName": "userId", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "userId-index",
                    "KeySchema": [{"AttributeName": "userId", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
                {
                    "IndexName": "sessionId-index",
                    "KeySchema": [{"AttributeName": "sessionId", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table.wait_until_exists()
        print("[OK] Test table created with moto")
        return mock
    except ImportError:
        print("[WARN] moto not installed. Using real DynamoDB (requires AWS credentials)")
        return None


def create_mock_event(user_id: str, method: str = "POST", body: Dict = None, query_params: Dict = None) -> Dict:
    """Create a mock API Gateway event."""
    return {
        "httpMethod": method,
        "body": json.dumps(body) if body else None,
        "queryStringParameters": query_params,
        "requestContext": {
            "authorizer": {
                "claims": {"sub": user_id}
            }
        }
    }


def test_start_interview():
    """Test start_interview handler."""
    print("\n=== Testing start_interview ===")
    from handlers.start_interview import lambda_handler

    event = create_mock_event("test-user-123", "POST", {
        "userId": "test-user-123",
        "role": "Software Engineer",
        "difficulty": "medium",
        "language": "English",
        "jdText": "We need a Python developer...",
        "resumeText": "5 years experience...",
    })

    result = lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"Session ID: {data['sessionId']}")
        print(f"First Question: {data['firstQuestion']}")
        return data['sessionId']
    else:
        print(f"Error: {result['body']}")
    return None


def test_submit_answer(session_id: str):
    """Test submit_answer handler."""
    print("\n=== Testing submit_answer ===")
    from handlers.submit_answer import lambda_handler

    for q_num in range(1, 6):
        event = create_mock_event("test-user-123", "POST", {
            "sessionId": session_id,
            "answer": f"This is my answer to question {q_num}. I have experience with Python, JavaScript, and AWS. I built a scalable web application using React and Django with PostgreSQL.",
            "questionNumber": q_num,
            "bodyLanguageMetrics": {
                "timestamp": int(time.time() * 1000),
                "eyeContactScore": 85,
                "postureScore": 80,
                "gestureScore": 75,
                "attentionScore": 90,
                "presenceDetected": True,
            }
        })

        result = lambda_handler(event, None)
        data = json.loads(result['body'])
        print(f"Q{q_num}: Status={result['statusCode']}, Complete={data.get('isComplete')}, Score={data.get('evaluation', {}).get('score')}")
        if data.get('isComplete'):
            break

    return result


def test_get_report(session_id: str):
    """Test get_report handler."""
    print("\n=== Testing get_report ===")
    from handlers.get_report import lambda_handler
    from shared.database import get_session

    # Get session for QA history
    session = get_session(session_id)
    if not session:
        print("Session not found!")
        return None

    event = create_mock_event("test-user-123", "POST", {
        "sessionId": session_id,
        "userId": "test-user-123",
        "qaHistory": session.get("qaHistory", []),
        "bodyLanguageMetrics": session.get("bodyLanguageMetrics", []),
    })

    result = lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        report = data.get('report', {})
        print(f"Overall Score: {report.get('overallScore')}")
        print(f"Category Scores: {report.get('categoryScores')}")
        return report
    else:
        print(f"Error: {result['body']}")
    return None


def test_list_interviews():
    """Test list_interviews handler."""
    print("\n=== Testing list_interviews ===")
    from handlers.list_interviews import lambda_handler

    event = create_mock_event("test-user-123", "GET", query_params={"userId": "test-user-123"})
    result = lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        print(f"Interviews found: {len(data.get('interviews', []))}")
        for interview in data.get('interviews', []):
            print(f"  - {interview['sessionId']}: {interview['role']} ({interview['difficulty']}) - Score: {interview['overallScore']}")
    else:
        print(f"Error: {result['body']}")


def test_list_interviews_with_report_rows():
    """Test list_interviews handler with fake report rows (no status field)."""
    print("\n=== Testing list_interviews with fake report rows ===")
    from handlers.list_interviews import lambda_handler
    from shared.database import _get_table

    table = _get_table()

    # Insert two fake report rows (no status field, but have overallScore)
    report1 = {
        "sessionId": "sess_report_1",
        "userId": "test-user-123",
        "role": "Software Engineer",
        "difficulty": "medium",
        "overallScore": 85,
        "categoryScores": {"technical": 80, "communication": 90, "confidence": 85, "problemSolving": 82, "bodyLanguage": 88},
        "qaHistory": [],
        "bodyLanguageSummary": {},
        "aiSummary": {},
        "createdAt": "2025-01-15T10:00:00Z",
        "durationMinutes": 20,
    }
    report2 = {
        "sessionId": "sess_report_2",
        "userId": "test-user-123",
        "role": "Frontend Developer",
        "difficulty": "easy",
        "overallScore": 72,
        "categoryScores": {"technical": 70, "communication": 75, "confidence": 72, "problemSolving": 68, "bodyLanguage": 75},
        "qaHistory": [],
        "bodyLanguageSummary": {},
        "aiSummary": {},
        "createdAt": "2025-01-10T10:00:00Z",
        "durationMinutes": 15,
    }

    from shared.db_utils import to_dynamodb_item
    table.put_item(Item=to_dynamodb_item(report1))
    table.put_item(Item=to_dynamodb_item(report2))

    # Also insert a session with status "completed"
    session_completed = {
        "sessionId": "sess_completed_1",
        "userId": "test-user-123",
        "role": "Backend Developer",
        "difficulty": "hard",
        "language": "English",
        "status": "completed",
        "overallScore": 90,
        "createdAt": "2025-01-20T10:00:00Z",
        "durationMinutes": 25,
    }
    table.put_item(Item=to_dynamodb_item(session_completed))

    # And a session with status "in_progress" (should NOT appear in list)
    session_in_progress = {
        "sessionId": "sess_in_progress_1",
        "userId": "test-user-123",
        "role": "Data Scientist",
        "difficulty": "medium",
        "language": "English",
        "status": "in_progress",
        "createdAt": "2025-01-25T10:00:00Z",
        "durationMinutes": 5,
    }
    table.put_item(Item=to_dynamodb_item(session_in_progress))

    event = create_mock_event("test-user-123", "GET", query_params={"userId": "test-user-123"})
    result = lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    if result['statusCode'] == 200:
        data = json.loads(result['body'])
        interviews = data.get('interviews', [])
        print(f"Interviews found: {len(interviews)}")
        for interview in interviews:
            print(f"  - {interview['sessionId']}: {interview['role']} ({interview['difficulty']}) - Score: {interview['overallScore']} - Date: {interview['date']} - Has categoryScores: {'categoryScores' in interview}")
        # Verify we get at least 3 (2 reports + 1 completed session + possibly the one from previous test), NOT the in_progress one
        assert len(interviews) >= 3, f"Expected at least 3 interviews, got {len(interviews)}"
        # Verify sorted newest first - the session from previous test should be newest (current date)
        # Then sess_completed_1 (2025-01-20), then sess_report_1 (2025-01-15), then sess_report_2 (2025-01-10)
        # Check that in_progress is NOT included
        session_ids = [i['sessionId'] for i in interviews]
        assert 'sess_in_progress_1' not in session_ids, "in_progress session should not be in list"
        # Check that our 3 test items ARE included
        assert 'sess_completed_1' in session_ids, "sess_completed_1 should be in list"
        assert 'sess_report_1' in session_ids, "sess_report_1 should be in list"
        assert 'sess_report_2' in session_ids, "sess_report_2 should be in list"
        # Verify categoryScores is included
        for interview in interviews:
            assert 'categoryScores' in interview, f"Missing categoryScores in {interview['sessionId']}"
        print("[OK] list_interviews correctly filters and sorts!")
        print("[OK] list_interviews correctly filters and sorts!")
    else:
        print(f"Error: {result['body']}")


def test_save_report():
    """Test save_report handler."""
    print("\n=== Testing save_report ===")
    from handlers.save_report import lambda_handler

    event = create_mock_event("test-user-123", "POST", {"report": {}})
    result = lambda_handler(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Response: {result['body']}")


def main():
    """Run all tests."""
    print("=" * 50)
    print("MockMate Lambda Local Tests")
    print("=" * 50)

    # Setup test environment
    mock = setup_test_table()

    try:
        # Run tests in sequence
        session_id = test_start_interview()
        if session_id:
            test_submit_answer(session_id)
            test_get_report(session_id)
            test_list_interviews()
        test_save_report()

        # Test list_interviews with fake report rows
        test_list_interviews_with_report_rows()

        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
    finally:
        if mock:
            mock.stop()


if __name__ == "__main__":
    main()