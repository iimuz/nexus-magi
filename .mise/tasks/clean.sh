#!/usr/bin/env bash
#MISE description="Clean this project."
#
# 設定を削除するためのスクリプト。

set -eu
set -o pipefail

echo "Clean frontend..."
cd frontend
  mise run clean
cd -

echo "Clean backend..."
cd backend
  mise run clean
cd -

echo "Clean api..."
cd api
  mise run clean
cd -

git clean -fdx ./node_modules
