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

- CI recommendations:
  - Use a pinned Docker image with KiCad 9 installed for headless `kicad-cli` runs to avoid macOS headless edge cases.
  - Emit a small `DAID.json` next to generated artifacts containing git sha, ISO8601 timestamp, and generator version.

Small checklist

- Add `tools/check_env.py` to validate local/CI env before running the pipeline.
- Document any divergence from these assumptions in this file.
