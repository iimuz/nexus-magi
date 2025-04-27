#!/usr/bin/env bash
#MISE description="Setup backend project."
#
# backendの環境構築を行うためのスクリプト。

set -eu
set -o pipefail

python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
