PYTHON ?= python3
VENV_DIR = .venv
PIP = $(VENV_DIR)/bin/pip
PY = $(VENV_DIR)/bin/python

.PHONY: venv gen erc pdf clean

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	if [ -f hardware/requirements.txt ]; then $(PIP) install -r hardware/requirements.txt; fi

gen: venv
	$(PY) projects/tile/gen_tile.py

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
