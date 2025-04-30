#!/usr/bin/env bash
#MISE description="Setup backend project."
#
# backendの環境構築を行うためのスクリプト。

set -eu
set -o pipefail

npm install --ci
