# quickstart.md

## Quickstart: simple project generation

1. Prepare a minimal `project.yaml` with ProjectType: "led_touch_grid" and required fields.
2. Run: `python -m src.cli.generate --config project.yaml --out ./out`
3. Expected: KiCad project files in `./out` and a validation report.

## Quickstart: hierarchical project generation

1. Prepare `project.yaml` with nested sheets and templates
2. Run the generate command and assert hierarchical schematic exported
