  #!/usr/bin/env bash
#MISE description="Bump dependencies."
#
# 依存関係のバージョンアップを行うスクリプト。

set -eu
set -o pipefail

git clean -dfx .venv

python -m venv .venv
.venv/bin/python -m ensurepip --upgrade
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev,test]"

.venv/bin/python -m pip freeze > requirements.txt
sed -i '' '/^-e /d' "requirements.txt"
