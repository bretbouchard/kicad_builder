# Byterover Handbook

## Layer 1: System Overview

**Project Purpose:**  
A modular capacitive touch button bar/grid system with addressable RGB LEDs, designed using KiCad 9 and powered by RP2040 microcontrollers. The system enables tileable PCB modules for interactive surfaces, combining capacitive touch sensing and addressable LED feedback.

**Tech Stack:**  
- Hardware design: KiCad 9.0  
- Firmware: MicroPython for RP2040  
- Build/automation: Python 3.11+, Makefile  
- Python tools: pytest, flake8, black, isort  
- Version control: Git

**Architecture:**  
- Modular, tileable PCB design  
- Dual RP2040 microcontroller per module (touch + LED control)  
- Hierarchical schematic structure (power, MCU, touch, LED, I/O, root)  
- Code generators for each schematic subsystem  
- Expansion via edge connectors  
- Test suite and automation for validation

**Key Technical Decisions:**  
- Use of standard components for manufacturability  
- PCB-etched capacitive touch pads  
- APA102/SK9822 addressable LEDs via SPI  
- I²C for inter-tile communication  
- Modular firmware and hardware for scalability

---

## Layer 4: Extension Points

**Configuration Classes:**  
- `LEDSheetConfig` in `led_sheet.py`: Centralizes LED sheet parameters (rows, columns, symbol/footprint, decoupling, etc.) for easy customization and future extension.
- `IOSheetConfig` in `io_sheet.py`: Encapsulates I/O sheet configuration for modular expansion.

**Extensible Patterns:**  
- All generator modules are designed for parameterization via config classes.
- `LEDSheetBuilder` class in `led_sheet.py` is a future extension point for advanced LED matrix features.
- BOM generation in `fabrication_output.py` supports plugin/CLI integration for supplier data.

**Customization Areas:**  
- Add new sheet generators by following the config-driven pattern.
- Extend config classes to support new hardware variants or features.
- Integrate additional plugins for BOM, validation, or simulation.

---
## Layer 3: Integration Guide

**Configuration:**  
- `.env` file for project metadata, KiCad version/paths, build flags, and dev settings
  - PROJECT_NAME, PROJECT_VERSION, KICAD_VERSION, KICAD_SYMBOL_LIB_PATH, KICAD_FOOTPRINT_LIB_PATH, GENERATE_NETLIST, GENERATE_SCHEMATIC, RUN_ERC_VALIDATION, GENERATE_PDF_EXPORT, DEBUG, LOG_LEVEL, TEST_COVERAGE

**Build & Automation:**  
- Makefile targets for generation, validation, export, docs, lint, format, and cleaning
- Example: `make gen`, `make validate`, `make export`, `make docs`, `make lint`, `make test`

**Python Entry Points:**  
- All code generators and tests are Python modules under `hardware.projects.led_touch_grid.gen` and `hardware.projects.led_touch_grid.tests`
- Example:  
  - `python -m hardware.projects.led_touch_grid.gen.power_sheet`  
  - `pytest hardware/projects/led_touch_grid/tests/`

**External Interfaces:**  
- KiCad 9.0 for schematic and PCB design
- MicroPython firmware for RP2040 MCUs

---
## Layer 2: Module Map

| Module                | Responsibility                                 |
|-----------------------|------------------------------------------------|
| netlist.py            | Netlist generation for the project             |
| power_sheet.py        | Power distribution schematic generator         |
| mcu_sheet.py          | Dual RP2040 MCU schematic generator            |
| touch_sheet.py        | Capacitive touch sensing schematic generator   |
| led_sheet.py          | LED control schematic generator                |
| io_sheet.py           | I/O connectivity schematic generator           |
| root_schematic.py     | Root schematic integration of all subsystems   |
| fabrication_output.py | Fabrication file generation (Gerber, BOM, etc) |
| pcb_placement.py      | PCB placement and layout automation            |
| touch_simulation.py   | Touch sensing simulation and validation        |

**Test Suite:**  
- Located in `hardware/projects/led_touch_grid/tests/`  
- Includes smoke tests, ERC validation, and sheet-specific tests

---
