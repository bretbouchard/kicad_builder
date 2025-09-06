# Auto-generated Makefile for button_grid
include .env

DAID_TIMESTAMP := 2025-09-05T05:46:26.544168+00:00
DAID_GIT_SHA := fc6096e
DAID_TOOL_VERSIONS := {"timestamp": "2025-09-05T05:46:26.544168+00:00", "git_sha": "fc6096e", "kicad_version": "9.0", "python_version": "3.11", "skidl_version": "1.0"}

.PHONY: gen verify pdf drc fab

gen:
	export PYTHONPATH="/Users/bretbouchard/apps/buttons" && \
        export KICAD9_SYMBOL_DIR="/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols" && \
        python -m hardware.projects.button_grid.gen.netlist && \
        python -m hardware.projects.button_grid.gen.schematic
	@echo "Schematics generated in kicad/"

verify:
	pytest -v hardware/projects/button_grid/tests/

pdf:
	kicad-cli sch export pdf hardware/projects/button_grid/kicad/root.kicad_sch -o out/schematic.pdf

drc:
	kicad-cli pcb drc hardware/projects/button_grid/kicad/board.kicad_pcb

fab:
	mkdir -p out/fab
	kicad-cli pcb export gerbers hardware/projects/button_grid/kicad/board.kicad_pcb -o out/fab
	kicad-cli pcb export drill hardware/projects/button_grid/kicad/board.kicad_pcb -o out/fab
	echo '# DAID Metadata
# Generated: 2025-09-05T05:46:26.544168+00:00
# Git SHA: fc6096e
# Tool Versions:
# - KiCad: 9.0
# - Python: 3.11
# - SKiDL: 1.0' > out/fab/DAID.md

version-check:
	@python tools/check_env.py

clean:
	rm -rf kicad/
	rm -rf out/
	rm -f *.log *.erc
