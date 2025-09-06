```prompt
---
mode: ask
---
Create or extend a SKiDL generator for a subsystem with hierarchical sheets.

Provide:
- short description of the subsystem and its responsibilities
- inputs: named interfaces (VCC, GND, I2C, SPI, UART, GPIOs, etc.) and pin roles
- constraints: voltages, current limits, timing, and other electrical constraints
- required symbols and footprints (name + preferred library and version if known)
- hierarchy plan: top-level sheet and child sheets with clear boundaries

Required artifacts:
- path and filename for the generator (e.g., `hardware/gen/<name>.py`)
- unit tests to add (pytest-friendly), including test vectors and expected netlists
- any scaffold/template changes needed (e.g., `tools/scaffold.py` hooks)

Success criteria:
- new generator file created or existing one extended and committed
- unit tests added and passing locally
- `make erc` and `make netlist` run without errors

Constraints & notes:
- prefer small, focused modules and reuse existing project conventions
- when uncertain about footprint versions, specify assumptions explicitly
- include suggested tradeoffs when choosing hierarchical boundaries

``` 
