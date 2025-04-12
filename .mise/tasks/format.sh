#!/usr/bin/env bash
#MISE description="Format."

python -m ruff format
dprint fmt
npx prettier --write "**/*.{yml,yaml}"
