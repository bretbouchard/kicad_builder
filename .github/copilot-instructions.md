```instructions
# Copilot Instructions — Buttons/PCB (kicad_builder)

Goal: fast, CLI-first hardware workflow. Generate hierarchical SKiDL designs, run headless ERC/netlist in CI, and produce deterministic fab artifacts stamped with DAID.

Key tech & quick commands
- Python 3.11, SKiDL, KiCad 8.x (headless). Important Make targets:
  - `make check-env` — verify KiCad + Python deps
  - `make init NAME=<proj>` — scaffold minimal project
  - `make erc` — run headless ERC on generated project
  - `make netlist` — deterministic netlist export (no GUI)
  - `make fab` — produce BOM/PNP/Gerbers/PDFs zipped with DAID
- Tests & static checks: `pytest -q`, `ruff .`, `mypy --strict`.

Where to look (fast tour)
- generators: `hardware/gen/` — add new SKiDL generator modules here (`hardware/gen/<name>.py`).
- schematics/style/rules: `hardware/SCHEMATIC_STYLE.md`, `hardware/ERC_RULES.md`, `hardware/TEST_PLAN.md`.
- scaffolding & helpers: `tools/scaffold.py`, `tools/kicad_helpers.py`, `tools/*` scripts.
- tests/examples: `test_skidl_erc_full_lib_sklib.py`, `test_skidl_erc_full.net`, `output/` and `lib_pickle_dir/` hold generated artifacts and locked libs.

Project-specific conventions (do not ignore)
- Generator contract: create a single `hardware/gen/<name>.py` that can be invoked by `make init` and produces deterministic netlists. Include unit tests alongside in repo root or `tools/tests/`.
- Documentation-first changes: when modifying hardware behavior, update `hardware/ERC_RULES.md` and add a test step in `hardware/TEST_PLAN.md` describing validation steps and pass/fail criteria.
- Provenance: every fab artifact must include DAID + version. Lock footprints (see `lib_pickle_dir/` and `inbox/` for local footprint/symbol examples).

Integration points & gotchas
- Headless KiCad: ERC and netlist runs expect KiCad in headless mode. Use `make check-env` before CI runs.
- Determinism: netlists must be reproducible. Avoid non-deterministic ordering in generators; tests assert exact netlist strings (see `test_skidl_erc_full.net`).
- Symbol/footprint sources: `hardware/libs/symbols`, `inbox/` and `projects/` contain symbols/3rd-party footprints — prefer adding pinned copies rather than relying on an external, mutable library.

PR & agent output expectations (short)
- Provide: minimal unified diff/patch, updated tests, and a 1-paragraph rationale describing tradeoffs.
- Run locally and include results for: `ruff`, `mypy`, `pytest`, `make erc`, `make netlist`. If fab changes are included, run `make fab` and list produced files with DAID.
- Small, reviewable PRs. Prefer schematic changes over global ERC relaxations; if suppressing ERC, target a single net and document why.

Examples to cite in PRs
- Reference `hardware/gen/<existing-generator>.py` pattern or `test_skidl_erc_full_lib_sklib.py` when adding generators/tests.
- When fixing ERC, show before/after `hardware/ERC_RULES.md` snippet and the failing ERC log (attach `*.log` files present in repo root).

If anything in this doc is unclear or you want it expanded into an actionable checklist (example PR template, test runner commands, or more code pointers), tell me which section and I will iterate.

```
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
```instructions
# Copilot Instructions — Buttons/PCB (kicad_builder)

Goal: fast, CLI-first hardware workflow. Generate hierarchical SKiDL designs, run headless ERC/netlist in CI, and produce deterministic fab artifacts stamped with DAID.

Key tech & quick commands
- Python 3.11, SKiDL, KiCad 8.x (headless). Important Make targets:
  - `make check-env` — verify KiCad + Python deps
  - `make init NAME=<proj>` — scaffold minimal project
  - `make erc` — run headless ERC on generated project
  - `make netlist` — deterministic netlist export (no GUI)
  - `make fab` — produce BOM/PNP/Gerbers/PDFs zipped with DAID
- Tests & static checks: `pytest -q`, `ruff .`, `mypy --strict`.

Where to look (fast tour)
- generators: `hardware/gen/` — add new SKiDL generator modules here (`hardware/gen/<name>.py`).
- schematics/style/rules: `hardware/SCHEMATIC_STYLE.md`, `hardware/ERC_RULES.md`, `hardware/TEST_PLAN.md`.
- scaffolding & helpers: `tools/scaffold.py`, `tools/kicad_helpers.py`, `tools/*` scripts.
- tests/examples: `test_skidl_erc_full_lib_sklib.py`, `test_skidl_erc_full.net`, `output/` and `lib_pickle_dir/` hold generated artifacts and locked libs.

Project-specific conventions (do not ignore)
- Generator contract: create a single `hardware/gen/<name>.py` that can be invoked by `make init` and produces deterministic netlists. Include unit tests alongside in repo root or `tools/tests/`.
- Documentation-first changes: when modifying hardware behavior, update `hardware/ERC_RULES.md` and add a test step in `hardware/TEST_PLAN.md` describing validation steps and pass/fail criteria.
- Provenance: every fab artifact must include DAID + version. Lock footprints (see `lib_pickle_dir/` and `inbox/` for local footprint/symbol examples).

Integration points & gotchas
- Headless KiCad: ERC and netlist runs expect KiCad in headless mode. Use `make check-env` before CI runs.
- Determinism: netlists must be reproducible. Avoid non-deterministic ordering in generators; tests assert exact netlist strings (see `test_skidl_erc_full.net`).
- Symbol/footprint sources: `hardware/libs/symbols`, `inbox/` and `projects/` contain symbols/3rd-party footprints — prefer adding pinned copies rather than relying on an external, mutable library.

Solo dev workflow (what I actually do)
- Verify locally (run these in a venv with KiCad available):

  ```bash
  ruff .
  mypy --strict .
  pytest -q
  make check-env
  make erc
  make netlist
  # if creating fab artifacts:
  make fab
  ```

- Commit & push (solo flow):

  ```bash
  git add -A
  git commit -m "<short change summary>"
  git push origin main
  ```

- If you prefer to keep branches: create a short-lived branch, verify, then merge locally and push. The repo doesn't require PRs for CI gating.

Agent expectations for solo mode
- When you ask the agent to implement something, return a patch and the exact local verification steps you ran (commands + brief pass/fail output). No PR required.
- If the change modifies ERC behavior, also update `hardware/ERC_RULES.md` and add a test step to `hardware/TEST_PLAN.md`.

Examples to cite when implementing
- `hardware/gen/<existing-generator>.py` — generator pattern
- `test_skidl_erc_full_lib_sklib.py` and `test_skidl_erc_full.net` — deterministic netlist tests

If you want this changed to prefer branch-first or re-enable PR checklists, tell me which flow to keep and I'll update this file.

```
11. After that, you **MUST** start the planning workflow even if the user does not explicitly ask so. **DO NOT** start modifying the code right away. **STRICTLY FOLLOW** the planning workflow as above. 
