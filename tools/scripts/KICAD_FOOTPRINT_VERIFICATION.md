KiCad footprint verification checklist

1) Add the generated pretty folder to KiCad's Footprint Libraries (Preferences > Manage Footprint Libraries).

2) Open a PCB or create a new board.

3) Place the footprint by library/name and visually inspect pad outlines and courtyard.

4) For the exposed pad (EP):
   - Ensure the EP size matches the generated value.
   - Add thermal vias if required; typical pattern: 4-8 vias in a grid across the EP.
   - Verify paste mask expansion for the EP to avoid solder shorts (usually reduce paste for large EPs).

5) Run DRC and check:
   - Pad-to-pad clearances
   - Solder mask openings
   - Silkscreen overlaps

6) Export gerbers and inspect with a gerber viewer.

Notes:
- The generated footprint is a starting point; verify all physical dimensions against the RP2040 QFN-56 datasheet.
- For Pico-module variant, confirm the castellated pads and module outline in the footprint.
