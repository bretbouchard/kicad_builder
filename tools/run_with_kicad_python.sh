#!/usr/bin/env bash
# Small helper to run Python scripts using KiCad's bundled python if available.
# Usage: tools/run_with_kicad_python.sh path/to/script.py [args...]
set -euo pipefail
repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"

# Read .env if present
if [ -f .env ]; then
  # shellcheck disable=SC1090
  set -o allexport
  . .env
  set +o allexport
fi

PYTHON_CMD=${KICAD_PYTHON:-}
if [ -z "$PYTHON_CMD" ]; then
  # try common macOS KiCad path
  maybe="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3"
  if [ -x "$maybe" ]; then
    PYTHON_CMD="$maybe"
  else
    echo "No KICAD_PYTHON set and default KiCad python not found."
    echo "Set KICAD_PYTHON in .env or export it in your shell to run KiCad scripts."
    exit 1
  fi
fi

exec "$PYTHON_CMD" "$@"
