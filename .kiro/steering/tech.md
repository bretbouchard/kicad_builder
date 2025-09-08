# Technology Stack

## Build System
- **Primary**: Make-based workflow with Python virtual environments
- **Package Management**: pip with requirements.txt files
- **Project Setup**: setuptools with `kicad_builder` package

## Core Dependencies
- **Python**: 3.11+ required
- **KiCad**: Version 9 with `kicad-cli` for ERC and PDF export
- **SKiDL**: 2.1.1 for circuit description and prototyping
- **Jinja2**: 3.1.4+ for template generation

## Development Tools
- **Testing**: pytest 7.4.0+
- **Linting**: ruff 0.12.0 with 120 character line length
- **Type Checking**: mypy 1.10.0 with strict mode
- **Code Formatting**: black with 120 character line length

## Common Commands

### Environment Setup
```bash
make venv          # Create virtual environment and install dependencies
make check-env     # Verify Python, modules, and KiCad installation
```

### Project Generation
```bash
make init NAME=<project>  # Scaffold new hardware project
make gen                  # Generate schematics from Python code
make netlist             # Generate netlists (alias for gen)
```

### Validation & Export
```bash
make erc            # Run KiCad electrical rules check
make pdf            # Export schematics to PDF
make verify-all     # Run all linting, type checking, tests, and validation
```

### Cleanup
```bash
make clean          # Remove output directory and virtual environment
```

## File Generation Pipeline
1. Python generators in `projects/<name>/gen_<name>.py`
2. Use `tools.kicad_helpers.Schematic` API
3. Output to `out/` directory with `.kicad_sch`, `.txt`, and JSON summaries
4. Validate with `kicad-cli sch erc`
5. Export PDFs with `kicad-cli sch export pdf`