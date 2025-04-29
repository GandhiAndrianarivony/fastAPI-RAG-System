#!/bin/bash

API_URL="http://localhost:4923/api/v1/chat"
ENGINE_ID="b3b5ff3eb80b43e49944f6f38551978d"
QUERY="What is the definition of Fine Number?"

curl -X POST http://localhost:4923/api/v1/chat \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the definition of Fine Number?",
    "engine_id": "b3b5ff3eb80b43e49944f6f38551978d"
  }'
