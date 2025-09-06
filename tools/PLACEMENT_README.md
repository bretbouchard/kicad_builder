Programmatic placement workflow
=================================

Files:
- `tools/generate_grid_placements.py` - generates CSV placement file,
  a minimal BOM summary, and a JSON ref->position mapping.
- `tools/kicad_place_from_csv.py` - helper to apply placements into an
  existing KiCad board using `pcbnew` (run inside KiCad's python env).

Quick start:

1. Generate placements for a 1-tile (8x8 pads, 4 LEDs/pad) layout:

   ```bash
   python3 tools/generate_grid_placements.py --tiles-x 1 --tiles-y 1
   ```

   This writes files into `projects/button_bar/placements/`.

2. Open your KiCad board that already contains the modules with the
   reference designators matching the CSV `ref` column.

3. From KiCad's scripting console (or using `kicad-cli` python), run:

   ```python
   from tools.kicad_place_from_csv import apply_from_csv
   apply_from_csv('/path/to/your_board.kicad_pcb',
                  'projects/button_bar/placements/grid_placements.csv')
   ```

Notes and limitations:
- The placer will only move modules that already exist on the board. It will
  not create new modules.
- Coordinates are in millimeters and the generator uses conservative defaults.
- After running the placer, always review placement and run DRC.

Create a new board from placements
----------------------------------

If you don't have an existing `.kicad_pcb`, you can create a new board skeleton
from the placements CSV. Run inside KiCad's Python console:

```python
from tools.kicad_create_board_from_csv import create_board_from_csv
create_board_from_csv('new_board.kicad_pcb',
                                 'projects/button_bar/placements/grid_placements.csv')
```

Notes:
- KiCad must be able to find the footprint libraries referenced by the CSV.
- The created board is a skeleton for placement and routing — verify footprints
   and run DRC after creation.

