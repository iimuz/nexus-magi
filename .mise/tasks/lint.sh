#!/usr/bin/env bash
#MISE description="Lint."

set -eu
set -o pipefail

echo "Lint backend files..."
cd backend
  mise run lint
cd -

echo "Lint markdown files..."
dprint check

echo "Lint yaml files..."
npx prettier --check "**/*.{yml,yaml}"

echo "Check spell..."
npx cspell lint . --no-progress
