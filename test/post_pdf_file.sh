#!/bin/bash

# Use first argument as the file path, or default to a sample path
FILE_PATH="${1:-path/to/file.pdf}"

curl -X POST http://localhost:4923/api/v1/files/37c99c2d49634e9f9a891be0e84f6e7a \
  -H "accept: application/pdf" \
  -F "files=@${FILE_PATH};type=application/pdf"
