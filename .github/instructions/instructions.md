# Copilot Instructions — Buttons/PCB repo

## Goal
CLI-first hardware workflow: generate hierarchical SKiDL → KiCad; run ERC+netlist in headless CI; produce fab artifacts and docs with DAID.

## Tech & Commands
- Python 3.11, SKiDL, KiCad 8.x (headless), Makefile targets:
  - `make init NAME=<proj>` → scaffold minimal project
  - `make erc` → headless ERC on the generated design
  - `make netlist` → deterministic netlist export
  - `make fab` → BOM/PNP/Gerbers/PDFs zipped with DAID
  - `make check-env` → verify KiCad + Python deps
- Tests: `pytest -q`; style: `ruff`, types: `mypy --strict`.

## Repo Conventions
- **Schematic style:** see `hardware/SCHEMATIC_STYLE.md`
- **ERC rules:** see `hardware/ERC_RULES.md`
- **Bring-up plan:** see `hardware/TEST_PLAN.md`
- **Docs & env:** `docs/ENV.md`
- **Provenance:** Every artifact includes DAID + version.

## What to Generate
- When asked for changes, return:
  - **Diff/patch** blocks, **updated Make targets/tests**, and a **1-paragraph rationale**.
  - If touching hardware, add/update `ERC_RULES.md` and test steps in `TEST_PLAN.md`.
- Prefer small, reviewable PRs. Always propose tests first.

## Review Criteria (Definition of Done)
- `ruff` + `mypy` clean
- Tests added/updated and passing
- `make erc` + `make netlist` deterministic (no GUI)
- If fab-facing, `make fab` produces DAID-stamped zip
- Update docs when commands or interfaces change
