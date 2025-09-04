QA checklist — RP2040 QFN-56 and vendor symbol onboarding

Purpose
- A concise step-by-step QA checklist to validate a new vendored symbol + footprint before production.

Preconditions
- Datasheet and mechanical drawing are saved in the repo (e.g. `docs/`).
- Vendored symbol, mapping JSON, and footprint are present under `tools/vendor_symbols/`.

Checklist
1) Pinmap sanity
  - Confirm `tools/vendor_symbols/mappings/*_pinmap.json` exists for the part.
  - Validate `pin_to_signal` covers all numbered pins in the datasheet.
  - Confirm `signal_to_pin` reverse mapping entries exist for multi-pin power rails.

2) Symbol checks (`*.lib`)
  - Symbol pin numbers match datasheet numbering and names.
  - `property "Footprint"` points to the canonical footprint name (Package_* or REPO-FOOTPRINT) used by generators.
  - Symbol fields (Value, Ref, Units) are correct and consistent.

3) Footprint checks (`*.kicad_mod` in `<name>.pretty/`)
  - Pad count equals number of pins in the `pinmap` and the symbol.
  - Pad numbering order follows the datasheet pin numbering (1..N) and matches symbol pin numbers.
  - Pad geometry (width, length) matches datasheet recommended pad dimensions (or your house rules).
  - Pad pitch and side spacing match the package drawing.
  - Exposed pad (EP) size matches datasheet; EP is defined as (pad "EP" smd ... (thermal) ...).
  - Solder paste layer (F.Paste) openings present and reviewed (consider 80–90% EP paste reduction if recommended).
  - Silk: reference and value placed outside copper and not overlapping pads.
  - Courtyard (optional) and Fab text present.

4) Net/EP connectivity
  - EP pad assigned to correct net (often GND). If EP must be tied to GND, ensure footprint net is set or documented.
  - Power pins mapped correctly to power flags in schematic (VCC/DVDD/IOVDD etc.).

5) Thermal via guidance
  - Add recommended via pattern as comments in footprint (do not automatically drill in the footprint unless pre-approved).
  - Document via size, tenting, and pitch for your board house.

6) KiCad integration & ERC/DRC
  - Add `tools/vendor_symbols/footprints/` pretty folders to KiCad footprint libraries (project or global) or copy to your standard library.
  - Load schematic in KiCad and verify symbol resolves to vendored lib and footprint.
  - Run ERC: fix any net or unit errors.
  - Create a PCB from the schematic (tool-assisted) and run DRC: check pad-to-pad clearance and silkscreen collisions.

7) Fab artifacts
  - After PCB placement, export Gerbers (F.Cu, B.Cu, F.Paste, B.Paste, F.Mask, B.Mask, F.Silk), drill file, and ODB/Pick-and-place CSV.
  - Verify Gerbers with a Gerber viewer and confirm EP/paste openings.

8) Sign-off
  - Document final footprint version string in repository (commit & tag message) and note any deviations from datasheet.
  - Add reviewer initials/date in the checklist once complete.

Acceptance criteria
- ERC/DRC pass without footprint/pin mapping issues relevant to the package.
- Fabrication files show correct pad geometry and EP paste opening as agreed.

Notes
- This checklist is intentionally conservative: finalize pad geometry with your PCB manufacturer if you need higher confidence (they can supply pad/paste tuning for assembly).
