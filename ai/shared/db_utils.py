"""
MockMate - DynamoDB Decimal Conversion Utilities
Handles conversion between Python floats/ints and DynamoDB Decimal types
"""

from decimal import Decimal
from typing import Any


def to_dynamodb(obj: Any) -> Any:
    """
    Recursively convert Python floats to Decimal for DynamoDB storage.
    DynamoDB requires Decimal for numeric values, not float.
    """
    if isinstance(obj, float):
        # Convert float to Decimal via string to avoid precision issues
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: to_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_dynamodb(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(to_dynamodb(item) for item in obj)
    return obj


def from_dynamodb(obj: Any) -> Any:
    """
    Recursively convert DynamoDB Decimal values back to Python int/float for JSON serialization.
    """
    if isinstance(obj, Decimal):
        # Convert to int if it's a whole number, else float
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    elif isinstance(obj, dict):
        return {k: from_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [from_dynamodb(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(from_dynamodb(item) for item in obj)
    return obj


def decimal_default(obj: Any) -> Any:
    """
    JSON default handler for Decimal objects.
    Use with json.dumps(obj, default=decimal_default)
    """
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def to_dynamodb_item(item: dict) -> dict:
    """
    Convert a complete item dict for DynamoDB put_item.
    Handles nested structures recursively.
    """
    return to_dynamodb(item)


def from_dynamodb_item(item: dict) -> dict:
    """
    Convert a DynamoDB item response back to Python types.
    """
    return from_dynamodb(item)