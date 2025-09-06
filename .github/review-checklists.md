## PR Checklist (code + hardware)
- [ ] ruff/mypy clean; new tests pass
- [ ] `make erc` and `make netlist` pass headless
- [ ] New nets named per SCHEMATIC_STYLE
- [ ] ERC_RULES.md updated when needed
- [ ] TEST_PLAN.md updated for new/changed behavior
- [ ] DAID/version stamped on generated artifacts

## Schematic Checklist
- [ ] Power entry + decoupling per device datasheets
- [ ] Net classes for LED power vs logic signals
- [ ] Sheet hierarchy + references consistent
- [ ] Deterministic netlist (no interactive fields)
