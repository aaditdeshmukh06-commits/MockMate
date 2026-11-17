"""
MockMate - DynamoDB Database Module
Module-level resource creation for reuse across Lambda invocations.
"""

import boto3
from typing import Any, Dict, List, Optional

from .utils import get_table_name, get_region
from .db_utils import to_dynamodb_item, from_dynamodb_item


# Module-level resources - reused across Lambda invocations
# This avoids recreating connections on every invocation (cold start optimization)
_dynamodb = None
_table = None


def _get_dynamodb_resource():
    """Get or create DynamoDB resource (singleton pattern for Lambda)."""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=get_region())
    return _dynamodb


def _get_table():
    """Get or create DynamoDB Table reference (singleton pattern for Lambda)."""
    global _table
    if _table is None:
        dynamodb = _get_dynamodb_resource()
        _table = dynamodb.Table(get_table_name())
    return _table


# ============================================================
# Session Operations
# ============================================================

def put_session(session_data: Dict[str, Any]) -> None:
    """Store interview session in DynamoDB."""
    table = _get_table()
    item = to_dynamodb_item(session_data)
    table.put_item(Item=item)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve interview session from DynamoDB."""
    table = _get_table()
    response = table.get_item(Key={"sessionId": session_id})
    item = response.get("Item")
    return from_dynamodb_item(item) if item else None


def update_session(session_id: str, updates: Dict[str, Any]) -> None:
    """Update specific fields of an interview session."""
    table = _get_table()

    # Build update expression
    update_expr = "SET "
    expr_values = {}
    expr_names = {}

    for i, (key, value) in enumerate(updates.items()):
        if i > 0:
            update_expr += ", "
        placeholder = f"#k{i}"
        value_placeholder = f":v{i}"
        update_expr += f"{placeholder} = {value_placeholder}"
        expr_names[placeholder] = key
        expr_values[value_placeholder] = to_dynamodb_item(value)

    table.update_item(
        Key={"sessionId": session_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )


# ============================================================
# Report Operations
# ============================================================

def put_report(report_data: Dict[str, Any]) -> None:
    """Store interview report in DynamoDB."""
    table = _get_table()
    item = to_dynamodb_item(report_data)
    table.put_item(Item=item)


def get_report(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve interview report from DynamoDB (using sessionId as GSI)."""
    table = _get_table()
    # Query by sessionId GSI - assuming GSI name is 'sessionId-index'
    response = table.query(
        IndexName="sessionId-index",
        KeyConditionExpression="sessionId = :sid",
        ExpressionAttributeValues={":sid": session_id},
        Limit=1,
    )
    items = response.get("Items", [])
    return from_dynamodb_item(items[0]) if items else None


# ============================================================
# History Operations
# ============================================================

def get_user_interviews(user_id: str) -> List[Dict[str, Any]]:
    """Get all completed interviews for a user."""
    table = _get_table()
    # Query by userId GSI - assuming GSI name is 'userId-index'
    response = table.query(
        IndexName="userId-index",
        KeyConditionExpression="userId = :uid",
        ExpressionAttributeValues={":uid": user_id},
        ScanIndexForward=False,  # Most recent first
    )
    items = response.get("Items", [])
    return [from_dynamodb_item(item) for item in items]


# ============================================================
# Utility Functions
# ============================================================

def delete_session(session_id: str) -> None:
    """Delete a session (for cleanup/testing)."""
    table = _get_table()
    table.delete_item(Key={"sessionId": session_id})


def health_check() -> Dict[str, str]:
    """Simple health check for the database connection."""
    try:
        table = _get_table()
        # Just describe the table to verify connection
        table.table_status
        return {"status": "healthy", "table": get_table_name()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}