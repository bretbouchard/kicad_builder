# Byterover Handbook for Buttons Project

## Layer 1: System Overview

**Project Purpose**: The Buttons project is a hardware automation system for designing modular LED capacitive touch button grids using Python-based KiCad workflows. It automates schematic generation, validation, and PCB layout for tileable modules with RP2040 microcontrollers, capacitive touch sensing, and addressable RGB LEDs. The focus is on music and creative interaction applications with scalable touch surfaces.

**Tech Stack**:
- **Language**: Python 3.x
- **Core Libraries**: skidl (schematic design), pcbnew (PCB handling from KiCad), jinja2 (templating), json, csv, pathlib
- **Hardware Tools**: KiCad integration for schematics (.kicad_sch), netlists, footprints (.kicad_mod), symbols (.lib)
- **Build/Testing**: pytest, ruff (linter), pre-commit hooks, GitHub Actions (CI)
- **Other**: simp_sexp (S-expression parsing for KiCad), requests (API calls for part lookup), subprocess (CLI integration)

**Architecture**: Hierarchical modular design with separation of concerns:
- **tools/**: Core utilities for KiCad helpers, library mapping, scaffolding, BOM generation, placement from CSV.
- **hardware/**: Project-specific implementations like button_grid with gen/ for schematic/netlist generation, tests/.
- **projects/**: Specific hardware projects like button_bar with components/symbols/footprints/, placements/.
- **.kiro/specs/**: Requirements, design, tasks for new features like led-touch-grid.
- **vendor_symbols/**: Imported third-party symbols and footprints.
- Workflow: Python scripts generate KiCad files → Validate with SKiDL ERC/DRC → Export Gerbers/BOM.

Key Technical Decisions: Use SKiDL for programmatic circuit design; hierarchical schematics for modularity; CSV-driven placement for grid automation; Docker for CI consistency.

## Layer 2: Module Map

**Core Modules**:

1. **tools.kicad_helpers** (tools/kicad_helpers.py): Provides Schematic and Symbol classes for generating KiCad S-expressions. Responsibilities: Build hierarchical schematics, add parts/pins/nets, write .kicad_sch files. Key files: Schematic.py, Symbol.py.

2. **tools.lib_map** (tools/lib_map.py): Resolves library IDs, validates KLC rules, manages Symbol dataclass. Responsibilities: Part lookup, footprint/symbol associations, metadata validation. Key files: lib_map.py, resolve_lib_id function.

3. **tools.scaffold** (tools/scaffold.py): Generates project structures with Jinja templates. Responsibilities: Create directories, populate Makefiles/READMEs with DAID metadata (git SHA, timestamps). Key files: scaffold.py.

4. **hardware.projects.button_grid.gen** (hardware/projects/button_grid/gen/): Project-specific generators for schematics/netlists. Responsibilities: Generate button grid circuits using helpers. Key files: schematic.py, netlist.py.

5. **tools.generate_grid_placements** (tools/generate_grid_placements.py): Automates component placement from grid specs. Responsibilities: CSV output for PCB placer with spacing/tolerance. Key files: generate_grid_placements.py.

**Data Layer**: JSON/CSV for pinmaps, metadata (e.g., pinmap.json, metadata_schema.json); No database, file-based.

**Utilities**: scripts/ for BOM/pinmap generation, tests/ with pytest; compat/ for KiCad version adapters.

## Layer 3: Integration Guide

**APIs and Interfaces**:
- **KiCad Integration**: pcbnew API for board creation/placement (kicad_create_board_from_csv.py, kicad_place_from_csv.py). Endpoints: create_board_from_csv(board_path, csv_path), apply_from_csv(board_path, csv_path).
- **SKiDL Circuit Building**: Part/Net/ERC from skidl; generate_netlist() for netlist export.
- **Part Lookup API**: resolve_lib_id() in lib_map.py; Optional HTTP via requests to external part databases (e.g., DigiKey).
- **Configuration Files**: metadata_schema.json (JSON schema for part metadata); rp2040.metadata.json (RP2040 pin/config); Makefile (build targets: gen, validate, export).
- **External Dependencies**: KiCad CLI (subprocess calls for ERC/DRC); Git for DAID metadata injection.
- **CLI Interfaces**: argparse-based scripts like gen_footprint.py, generate_bom.py, lookup_parts.py.

**Integration Points**: Run 'make gen' to trigger schematic → netlist → placement → outputs; CI via .github/workflows.

## Layer 4: Extension Points

**Design Patterns**: Dataclass for models (Symbol, HierarchicalPin); Factory for schematic building; Template method in generators (e.g., TileLayout.generate_positions()).

**Customization Areas**:
- Extend Schematic class for new sheet types (e.g., add power/led sheets).
- Plugin-like: Add to lib_map for new symbols/footprints; Override resolve_lib_id for custom part sources.
- Config: Edit metadata_schema.json for new fields; CSV inputs for placements (grid_placements.csv).
- Recent Changes: Vendor symbols imports, hierarchical support in kicad_helpers.

**Extension Guide**: To add new project: Run scaffold.py, implement gen/ scripts using helpers, add tests. For KiCad 8/9 compat: Update compat/kicad8_adapter.py.

## Validation Checklist
- [x] All 4 required sections present
- [x] Architecture pattern identified (Hierarchical modular)
- [x] At least 3 core modules documented
- [x] Tech stack matches project reality
- [x] Extension points or patterns identified