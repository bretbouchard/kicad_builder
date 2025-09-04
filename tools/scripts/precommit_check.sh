#!/usr/bin/env bash
# Local pre-commit check: run tests and component generator for PART
set -euo pipefail
PART=${1:-rp2040}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

echo "Running pytest..."
pytest -q

echo "Running component generator for $PART..."
cd "$ROOT/tools/scripts"
make component-add PART=$PART

echo "Precommit checks passed"
