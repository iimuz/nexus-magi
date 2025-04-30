#!/usr/bin/env bash
#MISE description="Format."

set -eu
set -o pipefail

echo "Format project files..."
dprint fmt
npx prettier --write "**/*.{yml,yaml}"

echo "Format api files..."
cd api
  mise run format
cd -

echo "Format backend files..."
cd backend
  mise run format
cd -
