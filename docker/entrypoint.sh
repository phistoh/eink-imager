#!/bin/sh
set -e

python -m einker.bootstrap

echo "✅ 'einker' initialized"

exec "$@"