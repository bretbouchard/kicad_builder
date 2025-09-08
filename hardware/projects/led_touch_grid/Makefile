# Makefile for led_touch_grid
DAID_TIMESTAMP := 2025-09-07T18:02:00.000000+00:00
DAID_GIT_SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
DAID_TOOL_VERSIONS := {"timestamp": "$(DAID_TIMESTAMP)", "git_sha": "$(DAID_GIT_SHA)", "kicad_version": "9.0", "python_version": "$(shell python --version 2>&1 | cut -d' ' -f2)"}

.PHONY: all gen clean verify test lint format help export validate docs

# Default target
all: gen verify

# Generate all project files
gen:
	python -m hardware.projects.led_touch_grid.gen.netlist
	python -m hardware.projects.led_touch_grid.gen.schematic

# Export fabrication files
export: gen
	python -m hardware.projects.led_touch_grid.gen.fabrication_output

# Run comprehensive validation
validate: gen
	python -m hardware.projects.led_touch_grid.tests.test_erc_suite
	pytest hardware/projects/led_touch_grid/tests/ -v --tb=short

# Generate documentation
docs:
	@echo "Generating project documentation..."
	@mkdir -p docs
	@echo "# LED Touch Grid Documentation" > docs/README.md
	@echo "Generated on: $(shell date)" >> docs/README.md
	@echo "Project Version: $(shell grep PROJECT_VERSION .env | cut -d'=' -f2)" >> docs/README.md

# Generate individual components
gen-power:
	python -m hardware.projects.led_touch_grid.gen.power_sheet

gen-mcu:
	python -m hardware.projects.led_touch_grid.gen.mcu_sheet

gen-touch:
	python -m hardware.projects.led_touch_grid.gen.touch_sheet

gen-led:
python hardware/projects/led_touch_grid/gen/led_sheet.py

gen-io:
	python -m hardware.projects.led_touch_grid.gen.io_sheet

gen-root:
	python -m hardware.projects.led_touch_grid.gen.root_schematic

# Clean generated files
clean:
	rm -rf hardware/projects/led_touch_grid/kicad/*.sch
	rm -rf hardware/projects/led_touch_grid/kicad/*.net
	rm -rf hardware/projects/led_touch_grid/kicad/*.pro
	find hardware/projects/led_touch_grid -name "*.pyc" -delete
	find hardware/projects/led_touch_grid -name "__pycache__" -delete

# Run tests
test:
pytest hardware/projects/led_touch_grid/tests/ -v
pytest hardware/projects/led_touch_grid/tests/test_led_sheet.py -v

# Run quick verification
verify:
	pytest -q hardware/projects/led_touch_grid/tests/

# Run linting
lint:
	flake8 hardware/projects/led_touch_grid/
	black --check hardware/projects/led_touch_grid/

# Format code
format:
	black hardware/projects/led_touch_grid/
	isort hardware/projects/led_touch_grid/

# Show help
help:
	@echo "LED Touch Grid Project Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all         - Generate files and run tests (default)"
	@echo "  gen         - Generate all project files"
	@echo "  gen-power   - Generate power distribution sheet"
	@echo "  gen-mcu     - Generate dual RP2040 MCU sheet"
	@echo "  gen-touch   - Generate capacitive touch sensing sheet"
	@echo "  gen-led     - Generate LED control sheet"
	@echo "  gen-io      - Generate I/O connectivity sheet"
	@echo "  gen-root    - Generate root schematic"
	@echo "  export      - Generate fabrication files (Gerber, BOM, etc.)"
	@echo "  validate    - Run comprehensive validation including ERC"
	@echo "  docs        - Generate project documentation"
	@echo "  clean       - Remove generated files"
	@echo "  test        - Run all tests with verbose output"
	@echo "  verify      - Run quick verification tests"
	@echo "  lint        - Check code style"
	@echo "  format      - Format code"
	@echo "  help        - Show this help message"
