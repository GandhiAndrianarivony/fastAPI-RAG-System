#!/bin/bash

curl -X POST http://localhost:4923/api/v1/chat \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the definition of Fine Number?",
    "id": "37c99c2d49634e9f9a891be0e84f6e7a"
  }'
