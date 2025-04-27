#!/usr/bin/env bash
#MISE description="Lint."

set -eu
set -o pipefail

echo "Lint python files..."
python -m ruff check .
