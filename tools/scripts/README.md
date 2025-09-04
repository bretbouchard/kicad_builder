tools/scripts — component onboarding utilities

This folder contains small utilities to convert CSV pinlists into a canonical
pinmap JSON, generate a minimal KiCad symbol, and produce a parameterized
QFN-56 footprint.

Usage examples

Generate a pinmap JSON from CSV and write to tools/vendor_symbols/mappings:

```bash
python3 generate_pinmap.py ../vendor_symbols/mappings/rp2040_qfn56_pinmap.csv --package RP2040 --out ../vendor_symbols/mappings/rp2040_pinmap.json
```

Generate a symbol from the pinmap:

```bash
python3 gen_symbol.py ../vendor_symbols/mappings/rp2040_pinmap.json ../vendor_symbols/REPO-rp2040.lib
```

Generate a footprint:

```bash
python3 gen_footprint.py --out ../vendor_symbols/footprints/REPO-rp2040-QFN56.pretty/REPO-rp2040-QFN56.kicad_mod
```

There's a convenience Makefile target `make component-add PART=rp2040` which
prefers `rp2040_qfn56_pinmap.json` if present and writes outputs under
`tools/vendor_symbols`.
