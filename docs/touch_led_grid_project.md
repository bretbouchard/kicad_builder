
# Modular Touch/LED Grid Project

## 1. Vision & Motivation
- **Why**:
  - Create a **large, modular, tileable button grid** for music and creative interaction.
  - Surface should feel continuous (no visible PCB seams).
  - Hardware only needs on/off touch + LEDs — software handles velocity and gestures.

- **Use Cases**:
  - Playing notes and rhythms like an instrument.
  - Editing patterns (click + drag for note length, drag up/down for pitch).
  - Visualizing complex structures with multi-color lighting.
  - Art, lighting, and interactive installations.

## 2. Hardware Concept
### 2.1 Pad Grid
- Target: **8×8 pads per tile**, each pad ~0.75–1.0 inch square.
- Tile multiple boards (e.g., 2×4 = 16×32 pads).
- Touch through acrylic overlay (smooth, durable).
- Touch = simple capacitive detection (on/off).

### 2.2 LED Density
- **Baseline**: 4 LEDs per pad (simple lighting).
- **Ambitious**: 16+ LEDs per pad (up to 64×64 LEDs per tile).
- Addressable RGB LEDs (APA102/SK9822, SPI interface).

### 2.3 Electronics
- **MCU**: Raspberry Pi RP2040.
  - One RP2040 for LED driving.
  - One RP2040 for touch sensing.
- **Power**: +5 V rail, bulk + decoupling caps, USB-C or barrel jack.
- **Connectivity**:
  - SPI for LEDs.
  - I²C or USB to host.
  - Optionally daisy-chain tiles.

## 3. Design Philosophy
- **Low cost, manufacturable**: APA102/SK9822, RP2040, standard FR-4.
- **Scalable**: One schematic per segment (16×16 LEDs), reused many times.
- **Maintainable**: Global labels for power/clock, hierarchical pins for data.

## 4. Electrical Architecture
### 4.1 Power
- Global +5V / GND nets.
- Bulk caps per tile, decoupling per LED.
- Fuse/ESD protection on input.

### 4.2 LED Drive
- **Option A (parallel)**: Each 16×16 block has its own DATA_IN. Fast, ~16 GPIOs.
- **Option B (chained)**: Blocks connected in series. Uses 1 GPIO, slower refresh.

### 4.3 Touch Sensing
- Capacitive pads etched into PCB.
- Connected to RP2040 GPIOs for sensing.
- Acrylic overlay provides smooth surface.

## 5. Mechanical / UI
- **Acrylic front panel**: Covers multiple tiles, hides seams, mounting hidden.
- **Tileable PCBs**: Each 8×8 pad tile is one PCB, edge connectors allow arrays.

## 6. Workflow in JITX
- Define LED+touch primitive → reused 64× per segment.
- Define 16×16 segment → reused 16× per tile.
- Define tile with RP2040 + power entry.
- Assemble multiple tiles into arrays.
- Parameterize pad size, LED density, tiling.

## 7. Implementation Steps
1. **Library setup** (APA102, RP2040, USB-C, passives).
2. **Segment schematic** (16×16 LED + pins).
3. **Tile schematic** (adds MCU + power).
4. **Mechanical design** (panel, acrylic).
5. **PCB layout** (grid placement, panelization).
6. **Firmware** (LED driver via SPI DMA, touch scan, USB HID/MIDI).
7. **Assembly & test** (start with one tile, then scale).

## 8. Key Tradeoffs
- **Parallel vs Chained LEDs**: GPIO usage vs refresh rate.
- **LED density**: 4 per pad vs 64 per pad.
- **Touch method**: direct capacitive vs ICs.
- **Scalability**: few large boards vs many tiles.

## 9. Roadmap
- **Phase 1**: Build 8×8 pad tile with 4 LEDs/pad (256 LEDs).
- **Phase 2**: Expand to 16×16 LEDs/pad (graphics).
- **Phase 3**: Tile multiple PCBs under one panel.
- **Phase 4**: Integrate firmware + host software.
