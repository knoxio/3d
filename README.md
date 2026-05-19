# 3d

Parametric PCB cases for FDM 3D printing, written in OpenSCAD.

## Layout

```
pcb_case.scad       library: one module that builds a base + snap-fit lid
boards/             one OpenSCAD file per board configuration
  esp_70x30.scad
  perfboard_20x80.scad
```

## Use

Open a board file in OpenSCAD. **F5** to preview, **F6** to render, then
export STL. The render selector at the bottom of each board file controls
what is drawn:

- `"base"`      base only
- `"lid"`       lid only (skirt down)
- `"all"`       base + lid side by side (default)
- `"assembled"` lid placed on top of base

To make a case for a new board:

1. Copy a file from `boards/`.
2. Edit the PCB dimensions, hole geometry, clearances, and cutouts.
3. Render and export STL.

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

## Snap-fit print tuning

After printing, if the lid is too tight or too loose, the knobs are:

- `lid_clearance` (0.3) — increase if the lid is too tight to insert
- `snap_ridge_depth` (0.4) — increase for stronger retention, decrease
  if too hard to close
- `skirt_height` (5.0) — taller skirt gives more guidance during insertion
