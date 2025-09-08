
# Hardware Bring‑Up & Test Plan

This document lists the minimal bring‑up and test steps for a newly built
button‑grid tile. Keep steps short and verifiable; include instruments,
expected results, and pass/fail criteria.

## 1 — Pre‑power inspection (visual)

- Verify solder joints, no shorts between power rails, connectors seated.
- Confirm populated decoupling caps on MCU power pins.

## 2 — Power smoke test

- Instrument: bench PSU limited to 100 mA, multimeter

- Steps:
  1. Set PSU to 3.3 V, current limit 100 mA.
  2. Connect to board VIN / 3V3 header.
  3. Observe current draw for 30 s.

- Pass: steady-state current < 50 mA and no heating/smoke.

- Fail: current > 100 mA or visible overheating — power off immediately.

## 3 — Basic functional checks

- Instrument: logic probe / scope, LED test jig

- Steps:
  1. With power applied, verify power rails measure 3.3 V ±5%.
  2. Run LED test: toggle LED driver lines via test pads or programming header.
  3. Verify at least one LED lights and brightness control functions.

- Pass: LEDs respond, no gross anomalies.

## 4 — Touch sensor baseline

- Instrument: oscilloscope or logic-level reader, mechanical probe

- Steps:
  1. Calibrate touch baseline (run calibration firmware or measure raw ADC).
  2. Confirm no false positives with hand away.
  3. Confirm press detection when touching pad.

- Pass: False positive rate ≈ 0; press detection within expected timing window.

## 5 — IO & Programming

- Steps:
  1. Connect programming/debug header.
  2. Attempt to read device ID / run a simple blink program.

- Pass: Device responds to programmer and runs basic firmware.

## 6 — Acceptance & Reporting

- Capture DAID metadata (commit SHA, timestamp, generator version) and
  attach logs/screenshots to the issue/PR that introduced the hardware.

- If any step fails, open an issue with: test step, observed behavior, logs,
  photo, and suggested mitigation.

---

This file is intended to be a minimal, copyable checklist to include in
the project `hardware/projects/<name>/TEST_PLAN.md` when a new project is
initialized via `make init`.
