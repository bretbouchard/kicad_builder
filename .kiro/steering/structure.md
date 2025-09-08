# Project Structure

## Repository Organization

### Core Directories
- **`tools/`** - Reusable generator libraries and helper modules
  - `kicad_helpers.py` - Main schematic generation API
  - `check_env.py` - Environment validation script
  - `scaffold.py` - Project template generator
  - `lib_map.py` - Symbol library mapping and resolution
  - `kicad_*.py` - KiCad-specific utilities (placement, board generation)

- **`projects/`** - Individual hardware project generators
  - `projects/<name>/gen_<name>.py` - Project-specific generator script
  - `projects/<name>/README.md` - Project documentation
  - Structure: Each project is self-contained with its own generator

- **`hardware/`** - Hardware-specific configurations and libraries
  - `requirements.txt` - Runtime Python dependencies (minimal)
  - `requirements-dev.txt` - Development dependencies
  - `libs/` - Custom KiCad symbol libraries
  - `projects/` - Alternative project location (legacy)

- **`out/`** - Generated artifacts (created by build process)
  - `<project>.kicad_sch` - KiCad schematic files
  - `<project>.sch.txt` - Human-readable schematic dump
  - `<project>_summary.json` - JSON project summary

### Configuration Files
- **`pyproject.toml`** - Python project configuration (black, ruff, flake8)
- **`setup.py`** - Package setup with tools dependencies
- **`Makefile`** - Primary build system interface
- **`.env`** - Environment variables (use `.env.example` as template)

## Code Organization Patterns

### Generator Scripts
- Located in `projects/<name>/gen_<name>.py`
- Import from `tools.kicad_helpers`
- Create `Schematic` objects with symbols, nets, and wires
- Call `write()` and `write_kicad_sch()` to generate outputs

### Symbol Management
- Use `lib_map.resolve_lib_id()` for consistent symbol references
- Format: `Symbol(lib="LibraryName", name="SymbolName", ref="U1")`
- Standard libraries: Device, Power, MCU, LEDs

### Output Conventions
- All generated files go to `out/` directory
- Multiple formats: `.kicad_sch`, `.txt`, `.json`
- Consistent naming: `<project_name>.<extension>`

## Development Workflow
1. Use `make init NAME=<project>` to create new project structure
2. Edit `projects/<project>/gen_<project>.py` with schematic logic
3. Run `make gen` to generate outputs
4. Validate with `make erc` and `make pdf`
5. Test with `make verify-all`