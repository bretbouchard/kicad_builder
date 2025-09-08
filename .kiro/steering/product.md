# Product Overview

This is a local-first KiCad 9 workflow system for hardware design automation. The project creates a Python-based toolchain that converts code into KiCad schematics, netlists, and supporting artifacts without relying on remote CI.

## Core Purpose
- Generate KiCad 9 schematics programmatically from Python code
- Create reusable hardware project templates and generators
- Provide local development workflow with validation (ERC, PDF export)
- Support multiple hardware projects within a single repository structure

## Key Components
- **Schematic Generation**: Python-based KiCad S-expression writers
- **Project Templates**: Scaffolding system for new hardware projects
- **Validation Pipeline**: ERC checks, PDF exports, and testing
- **Symbol Management**: Library mapping and symbol resolution system

## Target Use Cases
- RP2040-based hardware projects
- LED grid and touch interface designs
- Modular hardware tile systems
- Rapid prototyping with programmatic schematic generation