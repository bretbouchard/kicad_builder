SHELL := /bin/bash

PART ?= rp2040
MAPPINGS := ../vendor_symbols/mappings
OUT := ../vendor_symbols
PAD_W ?= 0.45
PAD_L ?= 0.9
EP ?= 4.4

.PHONY: component-add
component-add:
	@echo "Generating component for $(PART)"
	# prefer an explicitly named qfn56 mapping if present
	SRC=$(MAPPINGS)/$(PART)_qfn56_pinmap.json; \
	if [ ! -s "$$SRC" ]; then SRC=$(MAPPINGS)/$(PART)_pinmap.json; fi; \
	# try metadata file to override PAD defaults
	META=$(MAPPINGS)/$(PART).metadata.json; \
	if [ -f "$$META" ]; then eval $$(python3 read_metadata.py "$$META") ; fi; \
	mkdir -p $(OUT)/mappings $(OUT)/footprints; \
	python3 ./generate_pinmap.py "$$SRC" > $(OUT)/mappings/$(PART)_pinmap.json; \
	python3 ./gen_symbol.py $(OUT)/mappings/$(PART)_pinmap.json $(OUT)/REPO-$(PART).lib; \
	mkdir -p $(OUT)/footprints/REPO-$(PART)-QFN56.pretty; \
	python3 ./gen_footprint.py --out $(OUT)/footprints/REPO-$(PART)-QFN56.pretty/REPO-$(PART)-QFN56.kicad_mod --pad_w $(PAD_W) --pad_l $(PAD_L) --ep $(EP) --name REPO-$(PART)-QFN56
	@echo "Done. Review artifacts under $(OUT)"
