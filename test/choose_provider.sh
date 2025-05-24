#!/bin/bash

curl -X POST http://localhost:4923/api/v1/provider \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Ollama"
    }'