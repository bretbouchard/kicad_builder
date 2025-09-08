# Makefile for --component
DAID_TIMESTAMP := 2025-09-08T20:54:10.334008+00:00
DAID_GIT_SHA := 6b7229e
DAID_TOOL_VERSIONS := {"timestamp": "2025-09-08T20:54:10.334008+00:00", "git_sha": "6b7229e", "kicad_version": "9.0", "python_version": "3.11.11"}

.PHONY: gen verify
gen:
	python -m hardware.projects.--component.gen.netlist
	python -m hardware.projects.--component.gen.schematic

verify:
	pytest -q hardware/projects/--component/tests/