#!/usr/bin/env bash
#MISE description="Setup backend project."
#
# backendの環境構築を行うためのスクリプト。

set -eu
set -o pipefail

.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --upgrade -r requirements.txt
