#!/usr/bin/env bash
#MISE description="Clean this project."
#
# 設定を削除するためのスクリプト。

set -eu
set -o pipefail

git clean -fdx ./node_modules
