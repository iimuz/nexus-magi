#!/usr/bin/env bash
#MISE description="Bump dependencies."
#
# 依存関係のバージョンアップを行うスクリプト。

set -eu
set -o pipefail

echo "Update project root directory"
npm install --include=dev cspell@latest prettier@latest
dprint config update

echo "Update api"
cd api
  mise run update
cd -

echo "Update backend"
cd backend
  mise run update
cd -

echo "Update frontend"
cd backend
  mise run update
cd -
