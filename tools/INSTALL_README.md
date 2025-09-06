Preparing project-local KiCad libraries
======================================

This repository keeps footprints and symbols used by the `button_bar` project
under `projects/button_bar/components/footprints` and
`projects/button_bar/components/symbols`.

Run the helper script to copy them into project-local library folders that
KiCad can register easily:

```bash
./tools/install_project_kicad_libs.sh
```

After running:

- Footprints will be in `projects/button_bar/footprints.pretty` (KiCad pretty
  folder containing `.kicad_mod` files).
- Symbols will be in `projects/button_bar/symbols` (collection of `.kicad_sym`).

Register these folders in KiCad via Preferences → Manage Footprint Libraries
and Preferences → Manage Symbol Libraries, or add them to your project library
tables to keep them portable.

When running the Python board creation script (`tools/kicad_create_board_from_csv.py`),
ensure KiCad can locate the footprints by either registering the folders or
by adding them to the global/project library tables.
