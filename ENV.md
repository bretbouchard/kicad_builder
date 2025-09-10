# Environment and reproducibility notes

- Host: Apple M2 (32 GB RAM). Local GUI checks assume XQuartz is available for macOS.
- KiCad: baseline = 9.x. Generators and S-expression output target KiCad 9 by default.
- Python: recommend 3.11+. Pin exact version in CI (e.g. `python:3.11-slim`).
- SKiDL: pin a version in `pyproject.toml`/requirements when using advanced ERC rules.
- Env file: project currently uses an env file to set `KICAD_FOOTPRINTS_DIR` and `KICAD_PYTHON` for local runs. Example `.env`:

```sh
# Path to KiCad footprints (local or CI path)
KICAD_FOOTPRINTS_DIR=/usr/local/share/kicad/footprints
# Path to a KiCad Python executable (optional)
KICAD_PYTHON=/Applications/KiCad/kicad.app/Contents/SharedSupport/python3
```

Diagnostics from auto-registration
---------------------------------

When auto-registration of generators fails, the CLI will write a JSON
diagnostics file to the output directory (by default
`out/auto_register_diagnostics.json`). This file contains a list of
failure objects with the keys `path`, `type`, and `message` which CI
tooling can consume.


- CI recommendations:
  - Use a pinned Docker image with KiCad 9 installed for headless `kicad-cli` runs to avoid macOS headless edge cases.
  - Emit a small `DAID.json` next to generated artifacts containing git sha, ISO8601 timestamp, and generator version.

Small checklist

- Add `tools/check_env.py` to validate local/CI env before running the pipeline.
- Document any divergence from these assumptions in this file.

Developer dependencies
----------------------

This project relies on several Python packages for development and testing. Install them with:

```sh
python -m pip install -r hardware/requirements-dev.txt
```

The `hardware/requirements-dev.txt` includes `pydantic>=2.0,<3.0` which is required by the data models and validation engine.

Local-only testing & secrets
----------------------------

This repository is intended to run fully locally for tests and headless KiCad flows. Follow these steps:

1. Copy the example env file and add secrets locally (do NOT commit):

```sh
cp .env.example .env
# edit .env and paste real secrets (do not commit .env)
```

2. Install dev dependencies into your local venv:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r hardware/requirements-dev.txt
```

3. Run tests locally (use Kicad python for KiCad-specific tools if needed):

```sh
# run unit + integration tests
pytest tests/unit tests/integration -q

# to run full suite
python -m pytest -q

# to run a generator via KiCad python (example)
tools/run_with_kicad_python.sh hardware/projects/led_touch_grid/gen/mcu_sheet.py
```

4. CI: If you do not want tests to run in GitHub Actions, either remove the `repo-tests` job or make it conditional on a label/branch. I can help change the workflow to avoid using up CI minutes.

