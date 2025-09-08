# Design Document

## Overview

The LED Touch Grid system is a modular hardware platform that combines capacitive touch sensing with addressable RGB LED arrays. The system uses a Python-based KiCad workflow for automated schematic generation, validation, and PCB design. Each tile contains an 8×8 grid of touch-sensitive pads with corresponding LED arrays, controlled by dual RP2040 microcontrollers for optimal performance separation.

The design leverages the existing `tools/kicad_helpers.py` framework to generate hierarchical KiCad schematics programmatically, with automated validation through SKiDL ERC checks and custom electrical rules. The modular architecture allows tiles to be combined into larger interactive surfaces while maintaining signal integrity and power distribution.

## Architecture

### System Architecture

The system follows a hierarchical modular design with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Computer                            │
│                 (USB/I²C Interface)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  Tile Controller                           │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Touch MCU     │    │        LED MCU                 │ │
│  │   (RP2040)      │    │       (RP2040)                 │ │
│  │                 │    │                                 │ │
│  │ • 64 GPIO pins  │    │ • SPI LED Control               │ │
│  │ • Capacitive    │    │ • DMA Transfers                 │ │
│  │   sensing       │    │ • High refresh rate            │ │
│  │ • I²C to host   │    │ • Pattern generation           │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           │                           │                     │
│  ┌─────────┴───────────────────────────┴─────────────────┐   │
│  │              Power Distribution                       │   │
│  │  • 5V for LEDs    • 3.3V for MCUs                   │   │
│  │  • Bulk caps      • Decoupling                       │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Schematic Hierarchy

The design uses a hierarchical schematic structure with the following sheets:

1. **Root Sheet** (`root.kicad_sch`)
   - System overview and inter-sheet connections
   - Power input and distribution overview
   - Inter-tile connectivity

2. **Power Sheet** (`power.kicad_sch`)
   - Input protection and filtering
   - 5V to 3.3V regulation
   - Bulk capacitors and power distribution
   - ESD protection

3. **MCU Sheet** (`mcu.kicad_sch`)
   - Dual RP2040 microcontrollers
   - Crystal oscillators and decoupling
   - Programming interfaces (SWD)
   - GPIO allocation and routing

4. **Touch Sense Sheet** (`sense.kicad_sch`)
   - 64 capacitive touch pads (8×8 grid)
   - Touch pad routing to RP2040 GPIO
   - Reference ground plane considerations
   - Filtering and ESD protection

5. **LED Control Sheet** (`led.kicad_sch`)
   - APA102/SK9822 LED arrays (256 LEDs per tile)
   - SPI data and clock distribution
   - LED power distribution and decoupling
   - Parallel vs chained configuration options

6. **I/O Connectivity Sheet** (`io.kicad_sch`)
   - Inter-tile connectors
   - USB-C host interface
   - Programming connectors
   - Status indicators

## Components and Interfaces

### Microcontroller Selection

**Primary MCU: RP2040**
- **Touch MCU**: Dedicated to capacitive sensing
  - 64 GPIO pins for 8×8 touch grid
  - ADC for touch threshold calibration
  - I²C interface to host system
  - 133 MHz operation for responsive touch scanning

- **LED MCU**: Dedicated to LED control
  - SPI interface for APA102/SK9822 control
  - DMA support for high-speed LED updates
  - Multiple GPIO for parallel LED segment control
  - 133 MHz operation for smooth animations

### LED Subsystem

**LED Selection: APA102/SK9822**
- Addressable RGB LEDs with SPI interface
- 5V operation with 3.3V logic compatibility
- High refresh rates (>400 Hz for 256 LEDs)
- Consistent color reproduction

**LED Configuration Options:**
1. **Parallel Configuration**
   - 16 independent data lines (16×16 LEDs each)
   - Faster refresh rates (~1 kHz possible)
   - Higher GPIO usage (16 data + 1 clock)
   - Better fault isolation

2. **Chained Configuration**
   - Single data line for all 256 LEDs
   - Lower GPIO usage (1 data + 1 clock)
   - Slower refresh rates (~400 Hz)
   - Simpler routing

**Power Requirements:**
- Maximum current: 256 LEDs × 60mA = 15.36A @ 5V
- Typical current: 256 LEDs × 20mA = 5.12A @ 5V
- Bulk capacitance: 1000µF per tile minimum
- Decoupling: 100nF per 16-LED group

### Touch Sensing Subsystem

**Capacitive Touch Implementation:**
- PCB-etched copper pads (0.75" × 0.75" each)
- Direct connection to RP2040 GPIO pins
- Software-based capacitive sensing using RC timing
- Acrylic overlay for smooth user interface

**Touch Pad Specifications:**
- Pad size: 19mm × 19mm (0.75" × 0.75")
- Pad spacing: 20mm center-to-center
- Copper thickness: 1oz (35µm)
- Overlay thickness: 3mm acrylic maximum

**Sensing Algorithm:**
- RC discharge timing method
- Baseline calibration on startup
- Adaptive threshold adjustment
- Debouncing and filtering in software

### Power Distribution

**Power Architecture:**
- **Input**: 5V via USB-C or barrel jack
- **LED Power**: Direct 5V distribution with bulk capacitors
- **Logic Power**: 3.3V regulation from 5V (LDO or switching)
- **Current Capacity**: 20A input capability for full brightness

**Power Distribution Network:**
- 5V rail: 2oz copper, star topology from input
- 3.3V rail: 1oz copper, adequate for logic loads
- Ground: Solid ground plane with thermal vias
- Decoupling: 100nF ceramic + 10µF tantalum per IC

### Inter-Tile Connectivity

**Edge Connectors:**
- Power: 5V, 3.3V, GND (high current capacity)
- Data: SPI (MOSI, MISO, SCK), I²C (SDA, SCL)
- Control: Reset, enable, status signals
- Mechanical: Alignment pins and mounting holes

**Signal Integrity:**
- Controlled impedance for high-speed signals
- Termination resistors for long traces
- EMI filtering at tile boundaries
- Ground plane continuity across tiles

## Data Models

### Schematic Data Model

The design extends the existing `tools/kicad_helpers.py` framework:

```python
@dataclass
class HierarchicalPin:
    name: str
    direction: str  # "input", "output", "bidirectional", "power"
    at: Tuple[float, float]
    sheet_ref: str

@dataclass
class Sheet:
    name: str
    filename: str
    at: Tuple[float, float]
    size: Tuple[float, float]
    hierarchical_pins: List[HierarchicalPin]
    schematic: Schematic

class HierarchicalSchematic(Schematic):
    def __init__(self, title: str = "untitled"):
        super().__init__(title)
        self.sheets: List[Sheet] = []
        
    def add_sheet(self, sheet: Sheet) -> None:
        self.sheets.append(sheet)
        
    def connect_hierarchical_pins(self, parent_pin: str, child_pin: str) -> None:
        # Connect hierarchical pins between parent and child sheets
        pass
```

### Component Library Model

```python
@dataclass
class LEDComponent:
    part_number: str = "APA102"
    footprint: str = "LED_SMD:LED_APA102-2020"
    power_consumption: float = 0.06  # Amps at full brightness
    interface: str = "SPI"
    
@dataclass
class TouchPad:
    size: Tuple[float, float] = (19.0, 19.0)  # mm
    layer: str = "F.Cu"
    clearance: float = 0.2  # mm
    
@dataclass
class RP2040Config:
    crystal_freq: float = 12.0  # MHz
    gpio_allocation: Dict[str, List[int]]
    power_pins: List[int] = field(default_factory=lambda: [11, 22, 33, 44])
```

### Grid Layout Model

```python
@dataclass
class GridPosition:
    row: int
    col: int
    x: float  # mm
    y: float  # mm
    
@dataclass
class TileLayout:
    grid_size: Tuple[int, int] = (8, 8)
    pad_spacing: float = 20.0  # mm
    led_positions: List[GridPosition] = field(default_factory=list)
    touch_positions: List[GridPosition] = field(default_factory=list)
    
    def generate_positions(self) -> None:
        # Generate grid positions for LEDs and touch pads
        for row in range(self.grid_size[0]):
            for col in range(self.grid_size[1]):
                x = col * self.pad_spacing
                y = row * self.pad_spacing
                self.led_positions.append(GridPosition(row, col, x, y))
                self.touch_positions.append(GridPosition(row, col, x, y))
```

## Error Handling

### Schematic Generation Errors

**Symbol Resolution Errors:**
- Missing library references
- Undefined footprint assignments
- Invalid pin connections

**Error Handling Strategy:**
```python
class SchematicGenerationError(Exception):
    def __init__(self, message: str, component: str = None, sheet: str = None):
        self.message = message
        self.component = component
        self.sheet = sheet
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        context = []
        if self.sheet:
            context.append(f"Sheet: {self.sheet}")
        if self.component:
            context.append(f"Component: {self.component}")
        
        if context:
            return f"{self.message} ({', '.join(context)})"
        return self.message
```

### Validation Errors

**ERC Rule Violations:**
- Missing decoupling capacitors
- Multiple I²C pull-ups
- Unconnected power pins
- Hierarchical pin mismatches

**Custom Validation Rules:**
```python
def validate_power_decoupling(schematic: Schematic) -> List[str]:
    errors = []
    power_pins = find_power_pins(schematic)
    
    for pin in power_pins:
        nearby_caps = find_nearby_capacitors(pin, radius=5.0)  # 5mm radius
        if not any(cap.value == "100nF" for cap in nearby_caps):
            errors.append(f"Missing 100nF decoupling capacitor near {pin}")
    
    return errors

def validate_i2c_pullups(schematic: Schematic) -> List[str]:
    errors = []
    i2c_nets = find_i2c_nets(schematic)
    
    for net in i2c_nets:
        pullups = find_pullup_resistors(net)
        if len(pullups) == 0:
            errors.append(f"Missing pull-up resistors on {net.name}")
        elif len(pullups) > 1:
            errors.append(f"Multiple pull-up resistors on {net.name}")
        elif pullups[0].value not in ["1k", "2.2k", "4.7k", "10k"]:
            errors.append(f"Invalid pull-up value {pullups[0].value} on {net.name}")
    
    return errors
```

### PCB Generation Errors

**Placement Errors:**
- Component overlap detection
- Grid alignment validation
- Mechanical constraint violations

**DRC Error Handling:**
- Automated DRC rule loading
- Error categorization and reporting
- Suggested fixes for common violations

## Testing Strategy

### Unit Testing

**Schematic Generation Tests:**
```python
def test_hierarchical_schematic_generation():
    """Test that hierarchical schematics are generated correctly."""
    sch = HierarchicalSchematic("test_tile")
    
    # Add power sheet
    power_sheet = create_power_sheet()
    sch.add_sheet(power_sheet)
    
    # Add MCU sheet
    mcu_sheet = create_mcu_sheet()
    sch.add_sheet(mcu_sheet)
    
    # Connect power between sheets
    sch.connect_hierarchical_pins("power.5V_OUT", "mcu.5V_IN")
    
    # Generate and validate
    sch.write_kicad_sch("test_output")
    assert os.path.exists("test_output/test_tile.kicad_sch")
    
    # Validate hierarchical connections
    validate_hierarchical_connections(sch)

def test_led_grid_placement():
    """Test LED grid placement accuracy."""
    layout = TileLayout(grid_size=(8, 8), pad_spacing=20.0)
    layout.generate_positions()
    
    # Verify grid dimensions
    assert len(layout.led_positions) == 64
    
    # Verify spacing accuracy
    pos1 = layout.led_positions[0]  # (0,0)
    pos2 = layout.led_positions[1]  # (0,1)
    spacing = abs(pos2.x - pos1.x)
    assert abs(spacing - 20.0) < 0.01  # ±0.01mm tolerance
```

**ERC Validation Tests:**
```python
def test_power_decoupling_validation():
    """Test that power decoupling validation works correctly."""
    sch = create_test_schematic_with_rp2040()
    
    # Test missing decoupling capacitor
    errors = validate_power_decoupling(sch)
    assert len(errors) > 0
    assert "Missing 100nF decoupling capacitor" in errors[0]
    
    # Add decoupling capacitor
    add_decoupling_capacitor(sch, "U1", "100nF")
    
    # Test validation passes
    errors = validate_power_decoupling(sch)
    assert len(errors) == 0

def test_i2c_pullup_validation():
    """Test I²C pull-up resistor validation."""
    sch = create_test_schematic_with_i2c()
    
    # Test missing pull-ups
    errors = validate_i2c_pullups(sch)
    assert "Missing pull-up resistors" in errors[0]
    
    # Add correct pull-ups
    add_i2c_pullups(sch, "4.7k")
    errors = validate_i2c_pullups(sch)
    assert len(errors) == 0
    
    # Test multiple pull-ups error
    add_i2c_pullups(sch, "2.2k")  # Add second set
    errors = validate_i2c_pullups(sch)
    assert "Multiple pull-up resistors" in errors[0]
```

### Integration Testing

**End-to-End Workflow Tests:**
```python
def test_complete_tile_generation():
    """Test complete tile generation workflow."""
    # Generate schematic
    generator = TileGenerator("test_tile")
    generator.generate_all_sheets()
    generator.write_kicad_project("output/test_tile")
    
    # Validate ERC
    erc_results = run_skidl_erc(generator.schematic)
    assert erc_results.error_count == 0
    
    # Generate PCB
    pcb_generator = PCBGenerator("output/test_tile")
    pcb_generator.create_board_from_netlist()
    pcb_generator.place_components_from_csv("test_grid.csv")
    
    # Validate DRC
    drc_results = run_kicad_drc("output/test_tile/test_tile.kicad_pcb")
    assert drc_results.error_count == 0
    
    # Generate outputs
    generate_fabrication_outputs("output/test_tile")
    assert os.path.exists("output/test_tile/fab/gerbers.zip")
    assert os.path.exists("output/test_tile/fab/bom.csv")
```

### Hardware-in-Loop Testing

**Touch Sensing Validation:**
- Capacitance measurement verification
- Touch threshold calibration
- Response time measurement
- Cross-talk analysis between adjacent pads

**LED Control Validation:**
- Color accuracy verification
- Refresh rate measurement
- Power consumption validation
- Thermal performance testing

**System Integration Testing:**
- Multi-tile communication
- Power distribution validation
- EMI/EMC compliance testing
- Mechanical fit and finish verification