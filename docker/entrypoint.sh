#!/bin/sh
set -e

echo "Initializing file structure..."
python -m einker.setup

echo "Checking permissions..."
python -m einker.preflight

echo "✅ 'einker' OK"

exec "$@"