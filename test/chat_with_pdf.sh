#!/bin/bash

API_URL="http://localhost:4923/api/v1/chat"
ENGINE_ID="c0d9e272-4729-46ec-a9eb-1f07d24c1c97"
QUERY="What is the definition of Fine Number?"

response=$(curl -sS -X POST "$API_URL" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "'"$QUERY"'",
    "engine_id": "'"$ENGINE_ID"'"
  }')

# Check if curl succeeded
if [ $? -eq 0 ]; then
    echo "Success:"
    echo "$response" | jq .  # Pretty-print JSON response if jq is available
else
    echo "Error: API request failed"
    exit 1
fi