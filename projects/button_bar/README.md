Button Bar project
==================

This folder contains a minimal scaffold for the Button Bar PCB project.


What's included:

- `schematic/` — human-readable schematic sheets (placeholders) for top-level
  sheet, button matrix, and power/connectors.

- `components/` — symbol and footprint placeholders and notes for components

- `bom.csv` — a starter BOM template to be populated by the generator scripts

Next steps:

- Populate `components/symbols` with KiCad symbols or use `tools/scripts/gen_symbol.py`.

- Populate `components/footprints` with footprints or generate via `tools/scripts/gen_footprint.py`.

- Edit `schematic/*.sch.txt` to reflect the planned nets: VBUS/5V, VINT/3V3, GND,
  I2C/SPI/USB lines, matrix rows/cols, and any addressable LED power rails.
