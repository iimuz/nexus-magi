  #!/usr/bin/env bash
#MISE description="Bump dependencies."
#
# 依存関係のバージョンアップを行うスクリプト。

npm install --include=dev cspell@latest prettier@latest
dprint config update

