#!/usr/bin/env bash
set -euo pipefail

# Simple helper to prepare project-local KiCad footprint and symbol folders
# Copies .kicad_mod files into a .pretty folder and .kicad_sym files into a symbols
# folder under the project. Run this from the repository root.

PROJECT_DIR="projects/button_bar"
SRC_FP="$PROJECT_DIR/components/footprints"
DST_FP="$PROJECT_DIR/footprints.pretty"
SRC_SYM="$PROJECT_DIR/components/symbols"
DST_SYM="$PROJECT_DIR/symbols"

mkdir -p "$DST_FP"
mkdir -p "$DST_SYM"

echo "Copying footprints from $SRC_FP to $DST_FP"
shopt -s nullglob
fp_files=("$SRC_FP"/*.kicad_mod)
if [ ${#fp_files[@]} -eq 0 ]; then
  echo "No .kicad_mod files found in $SRC_FP"
else
  cp -v "$SRC_FP"/*.kicad_mod "$DST_FP"/
fi

echo "Copying symbols from $SRC_SYM to $DST_SYM"
sym_files=("$SRC_SYM"/*.kicad_sym)
if [ ${#sym_files[@]} -eq 0 ]; then
  echo "No .kicad_sym files found in $SRC_SYM"
else
  cp -v "$SRC_SYM"/*.kicad_sym "$DST_SYM"/
fi

echo
echo "Done. Project-local footprints:"
ls -1 "$DST_FP" || true
echo
echo "Project-local symbols:"
ls -1 "$DST_SYM" || true

cat <<'EOF'
Next steps to make KiCad load these libraries:

- Option A (quick, GUI):
  1. Open KiCad, go to Preferences → Manage Footprint Libraries.
  2. Choose 'Append with Wizard' or 'Append', and add the folder:
     <repo-root>/projects/button_bar/footprints.pretty
  3. For symbols: Preferences → Manage Symbol Libraries and add the
     <repo-root>/projects/button_bar/symbols folder or individual files.

- Option B (project-local, manual):
  - When creating a project in KiCad, you can point the project's library
    tables at these folders. See the KiCad docs; this keeps libraries local
    to the project and portable.

After registering the libraries, open your board or create a new one and the
footprints/symbols should be available for placement or module creation.
EOF
