#!/bin/bash
#
# MockMate DynamoDB Table Creation Script
# Creates the MockMateInterviews table with required GSIs
# Run with: bash scripts/create_table.sh
#

set -e

TABLE_NAME="MockMateInterviews"
REGION="us-east-1"

echo "Creating DynamoDB table: $TABLE_NAME in $REGION"

aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions \
        AttributeName=sessionId,AttributeType=S \
        AttributeName=userId,AttributeType=S \
    --key-schema AttributeName=sessionId,KeyType=HASH \
    --global-secondary-indexes \
        'IndexName=userId-index,KeySchema=[{AttributeName=userId,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
        'IndexName=sessionId-index,KeySchema=[{AttributeName=sessionId,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION"

echo "Waiting for table to become active..."
aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$REGION"

echo "Table created successfully!"
echo ""
echo "Table details:"
aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" --query 'Table.{TableName:TableName,TableStatus:TableStatus,KeySchema:KeySchema,GlobalSecondaryIndexes:GlobalSecondaryIndexes[*].{IndexName:IndexName,KeySchema:KeySchema,Projection:Projection}}' --output table