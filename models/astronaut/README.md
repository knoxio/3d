# Astronaut keyring

The Unspoken game's astronaut as a two-part printable keyring: white body,
black visor plug, hole through the helmet for the ring. Default 55 mm tall.

The source mesh is a rigged, low-poly game asset with open shells, so nothing
about it is printable as-is. `astronaut.py` drives Blender to fix that:

1. Swings the arms down from the T-pose (`arm_drop`, 35°). The swing is
   rigid, not skinned — the rig's smooth weights tear a 265-triangle
   shoulder apart. The arm root stays buried in the torso and the remesh
   welds it back on.
2. Widens anything thinner than `min_feature` (the aerials are 0.4 mm at this
   scale).
3. Voxel-remeshes to one watertight solid, closing the open shells.
4. Bores the keyring hole below the crown of the helmet.
5. Splits the visor (faces using the `Player_Helm` material) into its own
   part, shrunk by `visor_gap` so it drops into the recess with room for glue.
6. Decimates coplanar triangles and triangulates before export, so the STL is
   a few MB rather than 20.

## Parts

| File | Colour | Size | Volume |
| --- | --- | --- | --- |
| `astronaut-body.stl` | white | 34 × 27 × 55 | 13.2 cm³ |
| `astronaut-visor.stl` | black | 19.5 × 18.7 × 8.7 | 0.74 cm³ |

Both are single watertight solids, sitting on Z = 0 in print orientation:
the body standing, the visor face-down.

## Build

```bash
uv run --script models/astronaut/astronaut.py out/astronaut
```

Marked `build: manual`, so `mise run build` and CI skip it — it needs Blender
(`brew install --cask blender`) and the game repo checked out. `--src` points
at the FBX, `--height` scales the figure, and every tuning constant in
`DEFAULTS` has a matching flag.

| Flag | Default | Meaning |
| --- | --- | --- |
| `--height` | 55 | mm, overall height |
| `--arm-drop` | 35 | deg, arm swing from the T-pose |
| `--min-feature` | 1.6 | mm, thinnest part allowed |
| `--voxel` | 0.18 | mm, remesh resolution |
| `--visor-depth` / `--visor-gap` | 3 / 0.15 | mm, plug depth and glue clearance |
| `--keyring-dia` / `--keyring-margin` | 3.5 / 3.5 | mm, hole and solid helmet above it |
| `--simplify-angle` | 2 | deg, coplanar merge limit |

## Print

- P1S, PLA, 0.2 mm layers, 4 walls, 20 % infill.
- Body: white, standing as exported. Supports needed under the arms and the
  backpack — tree supports, and keep them off the helmet front.
- Visor: black, face-down as exported, no supports.
- Glue the visor into the helmet recess with a dab of CA.
- The hole has ~99 mm² of solid helmet above it, which is far more than a
  keyring needs; the weak direction is layer adhesion, so 4 walls matter more
  than infill.
- The aerial is the fragile part at this scale (1.6 mm). Raise
  `--min-feature` to 2–2.5 for a keyring that lives in a pocket.

## Source and licence

Mesh: "Low Poly Character" astronaut by **PULSAR BYTES**, from the Unity
Asset Store, used in `~/dev/gamedev/ucg/unspoken`. It is third-party and is
**not** in this repo: only the script that processes it lives here, and the
outputs land in gitignored `out/`. Print for personal use; do not redistribute
the mesh or sell prints of it.

## Assumptions

- The visor is the `Player_Helm` material in the FBX.
- The figure is printed at 55 mm; feature sizes above are in mm at that scale
  and rescale with `--height`.

## Status

draft — not yet printed.
