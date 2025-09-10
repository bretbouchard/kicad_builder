# Diagnostics collector

This small helper scans the repository for any `auto_register_diagnostics.json` files
(created by `src/services/auto_register.auto_register_generators`) and prints a
short summary useful in CI logs.

Usage:

```sh
# run with the project's Python (recommended)
python tools/collect_diagnostics.py

# or via Makefile if you have the venv set up
make diagnostics
```

Exit codes:
- 0: no diagnostics found
- 1: one or more diagnostics files found (the script prints summaries)

This is used in CI to collect and fail on auto-register problems while still
allowing the diagnostics JSON to be uploaded as an artifact for offline inspection.

Diagnostics format:
- Each diagnostics JSON is an array of failure objects.
- Fields you may see:
	- `path`: file path of the module
	- `type`: one of `import`, `register`, `register_callable`, `no_entrypoint`
	- `message`: human message describing the failure
	- `ts`: ISO timestamp when the failure was recorded
	- `traceback`: full formatted traceback (if available)
	- `snippet`: optional object with `start_line` and `lines` (small source snippet)

Annotating in CI:
- Run `python tools/annotate_diagnostics.py` to emit GitHub Actions annotation
	commands for each diagnostic (best-effort, non-fatal). CI workflows in this
	repo call the annotator before the collector so failures appear in the Checks UI.
