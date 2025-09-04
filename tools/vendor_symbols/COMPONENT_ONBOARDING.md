Component onboarding — sub-agent guide

Goal
- Give a repeatable procedure (and small automation ideas) so adding a new vendored symbol + footprint is fast, auditable, and scriptable.

Checklist (manual steps)
1) Find the datasheet and save a local copy under `docs/`.
2) Create a canonical pinmap JSON: `tools/vendor_symbols/mappings/<part>_pinmap.json`.
   - Fields: package, description, pin_to_signal, signal_to_pin, notes.
3) Create a symbol in `tools/vendor_symbols/REPO-<LIB>.lib`.
   - Name pins by datasheet numbers and assign signal names.
   - Add `(property "Footprint" "Package_<name>:<footprint_name>")`.
4) Author a footprint under `tools/vendor_symbols/footprints/<FOOTPRINT>.pretty/<FOOTPRINT>.kicad_mod`.
   - Use datasheet pad geometry. Add EP and paste openings.
5) Run the local generator and smoke-test schematic creation.
6) Import into KiCad and run ERC/DRC. Iterate footprint geometry if needed.

Automation ideas (sub-agent tasks)
- `extract_pinmap.py` — parse a spreadsheet or structured text from the datasheet and produce the canonical JSON.
- `symbol_from_pinmap.py` — generate a starter `*.lib` symbol from the pinmap JSON.
- `footprint_template.py` — generate a footprint `kicad_mod` using parameterized pad pitch/width/length/EP size.
- `qa_runner.sh` — run checks: pin count parity, pad numbering parity, and produce a short report.

Minimal implementation I recommend
1) `tools/scripts/generate_pinmap.py` — read a CSV of (pin,signal) and output the JSON mapping.
2) `tools/scripts/gen_symbol.py` — small Python program that reads the JSON and writes a `REPO-<LIB>.lib` symbol (minimal fields) suitable for manual polish.
3) `tools/scripts/gen_footprint.py` — parameterized footprint generator (pitch, pad_w, pad_l, ep_w, ep_h) that writes a kicad_mod.

Integration ideas
- Add a `make component-add PART=RP2040` to run generation steps and place generated artifacts into `tools/vendor_symbols/`.
- Store a per-component `metadata.yaml` with datasheet URL, version, and creation date for traceability.
- Optionally use Git hooks to require the QA checklist is filled before merge.

Example quick start (commands)
```bash
# generate pinmap from CSV
python3 tools/scripts/generate_pinmap.py docs/rp2040_pinmap.csv > tools/vendor_symbols/mappings/rp2040_qfn56_pinmap.json

# create symbol skeleton
python3 tools/scripts/gen_symbol.py tools/vendor_symbols/mappings/rp2040_qfn56_pinmap.json \
  --out tools/vendor_symbols/REPO-MCU.lib

# generate footprint
python3 tools/scripts/gen_footprint.py --package QFN-56 --pitch 0.5 --pad_w 0.45 --pad_l 0.9 \
  --ep 4.4x4.4 --out tools/vendor_symbols/footprints/REPO-MCU-QFN56.pretty/REPO-MCU-QFN56.kicad_mod
```

Where to start for automation
- Implement `generate_pinmap.py` first — it's the smallest win and makes symbol/footprint generation deterministic.
- Then add `gen_footprint.py` using a template with string substitution of pad coordinates.

Maintenance
- Keep `mappings/` JSON and `footprints/` pretty folders under source control.
- Record datasheet source and version in `metadata.yaml` per component.

If you want, I can implement the minimal scripts now (`generate_pinmap.py`, `gen_symbol.py`, `gen_footprint.py`) and wire a `Makefile` target `make component-add PART=rp2040` that runs the flow. Say “implement scripts” to proceed.
