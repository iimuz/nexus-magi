#!/usr/bin/env bash
#MISE description="Setup this project."
#
# 環境構築を行うためのスクリプト。

set -eu
set -o pipefail

echo "setup project root directory"
npm ci

echo "setup api"
cd api
  mise run setup
cd -

echo "setup backend"
cd backend
  mise run setup
cd -

echo "setup frontend"
cd frontend
  mise run setup
cd -
