#!/usr/bin/env bash
#MISE description="Lint."

set -eu
set -o pipefail

echo "Lint markdown files..."
dprint check

echo "Lint yaml files..."
npx prettier --check "**/*.{yml,yaml}"

echo "Check spell..."
npx cspell lint . --no-progress

echo "Lint api files..."
cd api
  mise run lint
cd -

echo "Lint backend files..."
cd backend
  mise run lint
cd -

echo "Lint frontend files..."
cd frontend
  mise run lint
cd -
