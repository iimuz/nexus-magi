#!/usr/bin/env bash
#MISE description="Setup this project."
#
# 環境構築を行うためのスクリプト。

set -eu
set -o pipefail

# setup node tools
npm install --ci
