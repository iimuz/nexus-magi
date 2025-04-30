#!/usr/bin/env bash
#MISE description="Format."

set -eu
set -o pipefail

npm run fix
