#!/usr/bin/env bash
#MISE description="Setup this project."
#
# 環境構築を行うためのスクリプト。

set -eu
set -o pipefail

echo "setup project root directory"
npm install --ci

echo "setup backend"
cd backend
  mise run setup
cd -

echo "setup fronend"
cd frontend
  npm install --ci
cd -
