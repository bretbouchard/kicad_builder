# LED Touch Grid Project

A modular capacitive touch button bar/grid system with addressable RGB LEDs, designed using KiCad 9 and powered by RP2040 microcontrollers.

## Overview

This project implements a tileable PCB module system that combines capacitive touch sensing with addressable RGB LED control. Each module contains:

- Dual RP2040 microcontroller architecture (touch sensing + LED control)
- APA102/SK9822 addressable RGB LED control via SPI
- PCB-etched capacitive touch pads
- Modular tile architecture for easy expansion

## Project Goals

### Primary Objectives
1. **Modular Design**: Create tileable PCB modules that can be combined into larger interactive surfaces
2. **Touch Sensing**: Implement reliable capacitive touch detection through acrylic overlays
3. **LED Control**: Provide smooth, addressable RGB LED feedback for user interactions
4. **Manufacturability**: Design for cost-effective production using standard components
5. **Scalability**: Support various grid sizes and configurations

### Technical Requirements
- **Touch Grid**: 8×8 capacitive touch pads per tile (19mm × 19mm each)
- **LED Array**: Up to 256 APA102/SK9822 LEDs per tile (4 LEDs per touch pad)
- **Power Distribution**: 5V for LEDs, 3.3V for logic with proper decoupling
- **Communication**: SPI for LEDs, I²C for inter-tile communication
- **Expansion**: Edge connectors for power and signal distribution between tiles

## Architecture

The system uses a hierarchical schematic design with the following main components:

1. **Power Distribution** - 5V for LEDs, 3.3V for logic, power sequencing
2. **Dual RP2040 MCU** - Touch sensing and LED control processors
3. **Capacitive Touch Sensing** - PCB-etched pads with touch detection
4. **LED Control** - APA102/SK9822 RGB LED matrix control
5. **I/O Connectivity** - Expansion headers and communication interfaces
6. **Root Schematic** - Integration of all subsystems

## Build Instructions

### Prerequisites

- KiCad 9.0 or later
- Python 3.11+
- Required Python packages (see `requirements.txt`)
- Git for version control

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd buttons/hardware/projects/led_touch_grid

# Generate all project files
make gen

# Run comprehensive validation
make validate

# Export fabrication files
make export

# Generate documentation
make docs
```

### Development Workflow

```bash
# Generate specific components
make gen-power      # Power distribution sheet
make gen-mcu        # Dual RP2040 MCU sheet
make gen-touch      # Capacitive touch sensing sheet
make gen-led        # LED control sheet
make gen-io         # I/O connectivity sheet
make gen-root       # Root schematic

# Run validation and tests
make verify         # Quick verification tests
make test           # Full test suite with verbose output
make validate       # Comprehensive validation including ERC

# Code quality
make lint           # Check code style
make format         # Format code

# Documentation and export
make docs           # Generate project documentation
make export         # Generate fabrication files

# Cleanup
make clean          # Remove generated files
```

### Environment Configuration

The project uses environment variables for configuration. Copy and customize `.env`:

```bash
# Project metadata
PROJECT_NAME=led_touch_grid
PROJECT_VERSION=0.1.0

# KiCad configuration
KICAD_VERSION=9.0
KICAD_SYMBOL_LIB_PATH=../../libs/symbols
KICAD_FOOTPRINT_LIB_PATH=../../libs/footprints

# Build configuration
GENERATE_NETLIST=true
GENERATE_SCHEMATIC=true
RUN_ERC_VALIDATION=true
GENERATE_PDF_EXPORT=true
```

### Advanced Usage

```bash
# Run specific generators manually
python -m hardware.projects.led_touch_grid.gen.netlist
python -m hardware.projects.led_touch_grid.gen.schematic

# Run specific sheet generators
python -m hardware.projects.led_touch_grid.gen.power_sheet
python -m hardware.projects.led_touch_grid.gen.mcu_sheet
python -m hardware.projects.led_touch_grid.gen.touch_sheet
python -m hardware.projects.led_touch_grid.gen.led_sheet
python -m hardware.projects.led_touch_grid.gen.io_sheet
python -m hardware.projects.led_touch_grid.gen.root_schematic

# Run simulation and validation
python -m hardware.projects.led_touch_grid.gen.touch_simulation
python -m hardware.projects.led_touch_grid.tests.test_erc_suite
```

## Project Structure

```
hardware/projects/led_touch_grid/
├── gen/                    # Code generators
│   ├── netlist.py         # Netlist generation
│   ├── schematic.py       # Schematic generation
│   ├── power_sheet.py     # Power distribution sheet
│   ├── mcu_sheet.py       # Dual RP2040 MCU sheet
│   ├── touch_sheet.py     # Capacitive touch sensing sheet
│   ├── led_sheet.py       # LED control sheet (APA102 chain, decoupling, bulk caps, validation, hierarchical pins)
│   ├── io_sheet.py        # I/O connectivity sheet
│   └── root_schematic.py  # Root schematic generator
├── kicad/                 # KiCad files and libraries
├── tests/                 # Test suite
│   ├── test_smoke.py      # Basic smoke tests
│   └── test_erc_suite.py  # ERC validation tests
├── Makefile              # Build automation
└── README.md             # This file
```

## Technical Specifications

### Electrical Requirements
- Operating Voltage: 5V (LEDs) / 3.3V (logic)
- Touch Sensing: 3.3V digital I/O
- LED Control: 5V power, 3.3V logic via level shifters
- Communication: SPI (LEDs), I2C (sensors), UART (debug)

### Mechanical Specifications
- Tileable module design
- Standard 2.54mm pitch headers
- Mounting holes for mechanical stability
- Compact footprint for dense arrays

### Software Architecture
- MicroPython firmware for RP2040
- Touch sensing algorithms
- LED animation and control
- Modular firmware design

## Design Goals

1. **Modularity** - Tileable design for easy expansion
2. **Simplicity** - Minimal component count for reliability
3. **Performance** - Responsive touch detection with smooth LED animations
4. **Manufacturability** - Standard components and processes
5. **Cost-effectiveness** - Optimized BOM for production

## Contributing

1. Follow the existing code style and structure
2. Add tests for new functionality
3. Update documentation as needed
4. Run the test suite before committing changes

## License

This project is part of the KiCad-based hardware design automation system.
