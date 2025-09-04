# Projects directory

This folder is intended to contain per-project generators and artifacts.

Structure guidance:
- `projects/<project-name>/gen.py` - project-specific generator that uses
  `../../tools/kicad_helpers.py` to emit an `out/` folder containing
  `.kicad_sch` (eventually), PDFs, and JSON summaries.
- `projects/<project-name>/README.md` - project-specific notes and build
  instructions.

Keep this directory focused on generated artifacts and per-project templates.
