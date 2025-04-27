#!/usr/bin/env bash
#MISE description="Format."

echo "Format project files..."
dprint fmt
npx prettier --write "**/*.{yml,yaml}"

echo "Format backend files..."
cd backend
  mise run format
cd -
