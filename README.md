# LED Touch Grid Project
# LED Touch Grid Project
## Developer quickstart

Install development dependencies (includes pydantic, jinja2, and test tooling):

```sh
python -m pip install -r hardware/requirements-dev.txt
```

Run unit and integration tests:

```sh
pytest tests/unit tests/integration -q
```

To run KiCad-specific scripts using KiCad's bundled Python, set `KICAD_PYTHON` in `.env` (see `ENV.md`) and use the helper:

```sh
tools/run_with_kicad_python.sh path/to/script.py
```

## Overview
This project...

## Architecture
Project components:
- Power system
- MCU control
- Touch sensing
- LED control

## Build Instructions
...


## Project Structure
Key components:
- gen/ - Generator scripts
- out/ - Output files
- tests/ - Test cases


## Technical Specifications
- Grid: 8x8 touch pads
- MCU: Dual RP2040
- LED: APA102 256 LEDs
- Power: 3.3V/5V dual rail


## Design Goals
- Modular architecture
- Scalable grid design
- Automated validation


## Diagnostics

When running the CLI (`kb-generate`), if auto-registration of generators
fails the CLI will return exit code 4 and write a diagnostics JSON file to
the output directory named `auto_register_diagnostics.json`. Collect this
file as an artifact in CI for debugging.

