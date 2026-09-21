# PCB cases

Parametric base + snap-fit lid for a bare PCB. Library: [`lib/pcb_case.scad`](../../lib/pcb_case.scad).

| File | Board |
| --- | --- |
| `esp_70x30.scad` | 70 × 30 mm ESP project board, 3 wall cutouts |
| `perfboard_20x80.scad` | 20 × 80 mm perfboard, no cutouts yet |

Parts: `base`, `lid` (exported separately). Set `part = "all"` or `"assembled"` in
OpenSCAD to see both.

## New board

1. Copy a board file in this directory.
2. Edit PCB dimensions, hole geometry, clearances and cutouts.
3. `make MODEL=pcb-cases`.

## Coordinate convention

The PCB origin `(0, 0)` is at corner **d**. `pcb_length` runs along +X,
`pcb_width` along +Y.

```
c -------------------- a
|                      |
|         PCB          |
|                      |
d -------------------- b
```

Walls of the case are named after the PCB edge they enclose:

- `bd`   wall along the low-Y edge  (between corners b and d)
- `ac`   wall along the high-Y edge (between corners a and c)
- `cd`   wall along the low-X edge  (between corners c and d)
- `ab`   wall along the high-X edge (between corners a and b)

Snap-fit wedges live on the `cd` / `ab` walls, so wall cutouts should go
on `bd` / `ac` to avoid interfering with the snap mechanism. The library
assumes `pcb_length >= pcb_width` — rotate dimensions if your board is
taller than wide.

## Cutouts

Each cutout is a 5-element list:

```
[wall, low_pos, width, z_above_pcb_top, height]
```

- `wall`            `"bd" | "ac" | "cd" | "ab"`
- `low_pos`         PCB-coord of the lower-coordinate end of the cutout
  (X for `bd`/`ac` walls; Y for `cd`/`ab` walls)
- `width`           extent along the wall direction
- `z_above_pcb_top` vertical offset from the top surface of the PCB
  (`0` = flush with PCB top)
- `height`          vertical extent of the cutout

## PCB hold-down

The lid has four corner posts (one at each PCB mounting hole) that drop
`top_clearance` down to press the PCB onto the standoff shoulders. Each
post has a small relief at its bottom so the standoff pin tucks inside.

Posts assume **at least 2 mm of clearance around each PCB mounting hole**
(so a 6 mm clear-circle diameter — components must not encroach). Toggle
with `pcb_hold_down`; tune the diameter with `corner_post_d` if your
clearance differs.

**Print orientation:** the corner posts hang below the lid skirt, so the
natural orientation is to print the lid upside-down (top plate flat on
the bed, posts pointing up).

## Snap-fit print tuning

After printing, if the lid is too tight or too loose, the knobs are:

- `lid_clearance` (0.3) — increase if the lid is too tight to insert
- `snap_ridge_depth` (0.4) — increase for stronger retention, decrease
  if too hard to close
- `skirt_height` (5.0) — taller skirt gives more guidance during insertion
