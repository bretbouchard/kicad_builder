## Project overview: Local-first KiCad 9 workflow

### Goal
Create a small, reusable local workflow that converts Python code into
KiCad 9 schematics and supporting artifacts (PDFs, netlists, JSON summaries)
without relying on remote CI. This is a durable foundation you can reuse for
multiple hardware projects.

### What we build first

- A tiny `tools/kicad_helpers.py` writer library (starter scaffold already in
  the repo).

- A `projects/<project>/gen.py` generator template that uses the helper API and
  emits `out/<project>.kicad_sch` (eventually) and a JSON summary.

- A local `Makefile` with `venv`, `gen`, `erc`, `pdf`, and `fab` targets.

### Tooling (local)

- Python 3.11+ (virtualenv)

- KiCad 9 (kicad-cli) available locally

- Optional: `skidl` for quick prototyping (`pip install skidl`)

- Optional: `kikit` for panelization and gerbers

### Workflow (developer)

1. Create and activate a Python virtualenv.

2. Edit `projects/<project>/gen.py` to describe your parts and placements.

3. Run `make gen` to generate `out/` artifacts.

4. Run `make erc` and `make pdf` to validate and export human-readable
  schematics.

### Repository layout (recommended)

- `tools/` - reusable generator libraries and helpers

- `projects/` - project-specific generators and artifacts

- `docs/` - design docs and onboarding

### Next steps (what I can implement now)

1. Add a `projects/tile/gen_tile.py` generator that creates a one-tile
  schematic (RP2040 + pads + a few LEDs) using `tools/kicad_helpers.py`.

2. Add a `Makefile` with the targets listed above.

3. Run a local smoke test: generate outputs and attempt `kicad-cli` export to
  PDF (requires KiCad 9 installed locally).

### Notes on symbol libraries and KiCad versions

- We'll target KiCad 9 S-expressions. KiCad sometimes changes lib symbol
  names between versions; to keep the repo portable we can either vendor the
  small set of symbols we use or include a mapping layer in the generator.

If you'd like, I can implement `projects/tile/gen_tile.py` and a `Makefile`
next. Tell me if you want me to move/remove `Buttons_bar/` now or leave it
in place for the moment.
