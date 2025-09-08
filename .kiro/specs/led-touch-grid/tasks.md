# Implementation Plan

- [x] 1. Extend schematic generation framework for hierarchical designs
  - [x] Implement `HierarchicalSchematic` class extending existing `Schematic` class
  - [x] Add `Sheet` and `HierarchicalPin` data classes for multi-sheet support
  - [x] Create methods for connecting hierarchical pins between parent and child sheets
  - [x] Write unit tests for hierarchical schematic generation and pin connections
  - [x] Add ERC validation for hierarchical connections
  - [x] Add power decoupling validation
  - [x] Add I2C pull-up resistor validation
  - [x] Implement comprehensive error handling and validation
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Create LED touch grid project scaffold and structure
  - Use existing `tools/scaffold.py` to create `hardware/projects/led_touch_grid/` project structure
  - Create project-specific Makefile with targets for generation, validation, and export
  - Set up directory structure for generators, sheets, tests, and output files
  - Initialize project README with goals and build instructions
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 3. Implement power distribution sheet generator
  - Create `gen/power_sheet.py` to generate power management schematic
  - Add 5V input protection, filtering, and bulk capacitor placement
  - Implement 3.3V regulation circuitry with proper decoupling
  - Define hierarchical pins for power distribution to other sheets
  - Write validation tests for power sheet ERC compliance
  - _Requirements: 1.1, 2.2, 7.1_

- [ ] 4. Implement dual RP2040 MCU sheet generator
  - Create `gen/mcu_sheet.py` for dual RP2040 microcontroller schematic
  - Add crystal oscillators, decoupling capacitors, and programming interfaces
  - Implement GPIO allocation for touch sensing (64 pins) and LED control (16+ pins)
  - Define hierarchical pins for GPIO connections to touch and LED sheets
  - Create validation rules for proper RP2040 power pin decoupling
  - _Requirements: 1.1, 2.2, 3.5, 4.2_

- [ ] 5. Create capacitive touch sensing sheet generator
  - Create `gen/touch_sheet.py` for 8×8 capacitive touch pad array
  - Implement PCB touch pad generation with proper sizing (19mm × 19mm)
  - Route touch pads to RP2040 GPIO pins with proper spacing
  - Add ESD protection and filtering components for touch inputs
  - Write tests for touch pad placement accuracy and GPIO allocation
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Implement LED control sheet generator
  - Create `gen/led_sheet.py` for APA102/SK9822 LED array schematic
  - Support both parallel (16 data lines) and chained (1 data line) configurations
  - Implement power distribution and decoupling for 256 LEDs per tile
  - Add SPI routing from RP2040 to LED arrays with proper signal integrity
  - Create validation for LED power requirements and decoupling placement
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 7. Create I/O connectivity sheet generator
  - Create `gen/io_sheet.py` for inter-tile and host connectivity
  - Implement edge connectors for power, SPI, and I²C signals between tiles
  - Add USB-C host interface with proper signal routing
  - Include programming connectors (SWD) and status indicators
  - Design mechanical alignment features for tile interconnection
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 8. Implement root schematic generator and integration
  - Create `gen/root_schematic.py` to generate main schematic with all sheets
  - Integrate all child sheets (power, MCU, touch, LED, I/O) into hierarchical design
  - Connect hierarchical pins between sheets for power, data, and control signals
  - Generate complete KiCad project file (.kicad_pro) with proper sheet references
  - Write integration tests for complete schematic generation workflow
  - _Requirements: 1.1, 1.3, 1.4_

- [ ] 9. Extend ERC validation with custom electrical rules
  - Extend existing validation framework with LED touch grid specific rules
  - Implement power decoupling validation for RP2040 and LED power pins
  - Add I²C pull-up resistor validation for inter-tile communication
  - Create hierarchical pin connection validation between sheets
  - Write comprehensive test suite for all custom ERC rules
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 10. Create component library and symbol mapping
  - Extend `tools/lib_map.py` with LED touch grid specific components
  - Add RP2040, APA102/SK9822, and touch-specific component definitions
  - Implement footprint associations for all components
  - Create vendor symbol imports for specialized components
  - Validate symbol library completeness with KiCad compatibility tests
  - _Requirements: 1.4, 3.1, 4.1_

- [ ] 11. Implement automated PCB grid placement system
  - Create `gen/pcb_placement.py` for automated component placement
  - Implement CSV-based grid placement with 20mm spacing and ±0.01mm tolerance
  - Add support for LED and touch pad grid alignment
  - Create placement validation and conflict detection
  - Write tests for placement accuracy and grid alignment
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 12. Create fabrication output generation system
  - Implement automated Gerber, drill, and pick-and-place file generation
  - Add DRC validation against manufacturing rules before output generation
  - Create BOM generation with part numbers, quantities, and supplier information
  - Implement DAID metadata injection for traceability (git SHA, timestamp, versions)
  - Write tests for fabrication output completeness and accuracy
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 13. Implement touch circuit simulation and validation
  - Create `gen/touch_simulation.py` for RC circuit analysis
  - Model capacitive touch pad characteristics and frequency response
  - Validate touch sensitivity and signal-to-noise ratio calculations
  - Generate simulation plots and component value recommendations
  - Write tests for simulation accuracy and parameter validation
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 14. Create continuous integration workflow
  - Implement GitHub Actions workflow for automated hardware validation
  - Add CI targets for schematic generation, ERC validation, and PDF export
  - Create artifact archival for generated schematics, BOMs, and fabrication files
  - Implement Docker-based CI environment for consistent tool versions
  - Write CI tests for complete workflow validation and error reporting
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 15. Implement project template and documentation system
  - Create comprehensive project documentation with build instructions
  - Implement template system for new LED touch grid variants
  - Add example configurations for different grid sizes and LED densities
  - Create troubleshooting guide for common validation and build issues
  - Write user guide for customizing and extending the LED touch grid system
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
