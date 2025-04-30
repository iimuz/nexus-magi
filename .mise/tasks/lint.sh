#!/usr/bin/env bash
#MISE description="Lint."

set -eu
set -o pipefail

echo "Lint markdown files..."
dprint check

echo "Lint yaml files..."
npm run check

echo "Check spell..."
npm run lint:spell

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
