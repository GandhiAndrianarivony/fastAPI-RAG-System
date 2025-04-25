#!/bin/bash

# Use first argument as the file path, or default to a sample path
FILE_PATH="${1:-path/to/file.pdf}"

curl -X POST http://localhost:4923/api/v1/files \
  -H "accept: application/pdf" \
  -F "files=@${FILE_PATH};type=application/pdf"
