PYTHON ?= python3
VENV_DIR = .venv
PIP = $(VENV_DIR)/bin/pip
PY = $(VENV_DIR)/bin/python

.PHONY: venv gen erc pdf clean verify-all netlist
.PHONY: check-env init

.PHONY: diagnostics
diagnostics:
	$(PY) tools/collect_diagnostics.py

check-env:
	$(PY) tools/check_env.py

init:
	$(PY) tools/scaffold.py $(NAME)


.PHONY: check-env-allow

check-env-allow:
	BUTTONS_IGNORE_PYTHON_CHECK=1 $(PY) tools/check_env.py

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	if [ -f hardware/requirements.txt ]; then $(PIP) install -r hardware/requirements.txt; fi
	if [ -f hardware/requirements-dev.txt ]; then $(PIP) install -r hardware/requirements-dev.txt; fi

gen: gen-power gen-mcu gen-touch gen-led gen-io gen-root
	$(PY) projects/tile/gen_tile.py

netlist: gen

.PHONY: verify-all
verify-all: venv
	$(VENV_DIR)/bin/ruff . || true
	$(VENV_DIR)/bin/mypy --strict . || true
	$(VENV_DIR)/bin/pytest -q || true
	$(MAKE) check-env
	$(MAKE) erc
	$(MAKE) netlist

erc:
	@if command -v kicad-cli >/dev/null 2>&1; then \
		kicad-cli sch erc out/tile.kicad_sch || true; \
	else \
		echo "kicad-cli not found; install KiCad 9 to run ERC."; \
	fi

pdf:
	@if command -v kicad-cli >/dev/null 2>&1; then \
		kicad-cli sch export pdf out/tile.kicad_sch -o out/ || true; \
	else \
		echo "kicad-cli not found; install KiCad 9 to export PDFs."; \
	fi

clean:
	rm -rf out $(VENV_DIR)

gen-power:
	python3 gen/power_sheet.py


gen-mcu:
	python3 gen/mcu_sheet.py

gen-touch:
	python3 gen/touch_sheet.py

gen-led:
	python3 gen/led_sheet.py

gen-io:
	python3 gen/io_sheet.py

gen-root:
	python3 gen/root_schematic.py


test:
	pytest hardware/projects/led_touch_grid/tests/


verify:
	echo 'Verification not implemented'


lint:
\tflake8 . --ignore=E501,W503

format:
\tblack .

help:
\t@echo "Available targets:"
\t@echo "  gen       - Generate all schematics"
\t@echo "  test      - Run tests"
\t@echo "  lint      - Check code style"
\t@echo "  format    - Format code"
\t@echo "  verify    - Run verification checks"
