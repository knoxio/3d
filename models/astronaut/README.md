# Astronaut keyring

The Unspoken game's astronaut as a three-part printable keyring: white body,
black visor plug, and a separate backpack that prints lying down. Default
55 mm tall, with chunkier proportions than the game mesh so it reads as a
keyring rather than a shrunken character.

The source mesh is a rigged, low-poly game asset with open shells, so nothing
about it is printable as-is. `astronaut.py` drives Blender to fix that:

1. Swings the arms down from the T-pose (`arm_drop`, 35°). The swing is
   rigid, not skinned — the rig's smooth weights tear a 265-triangle
   shoulder apart. The arm root stays buried in the torso and the remesh
   welds it back on.
1. Fattens the figure (`plump`, 1.18 across against height) and grows the
   helmet about the neck (`head_scale`, 1.1).
1. Splits the backpack off: the components sitting behind the torso, minus
   the hip pods, which are behind it but far off the centreline. The pack is
   then subtracted from an inflated copy of the body, so its front face
   conforms to the torso with a `boss_fit` gap, and a locating cone is added
   to the body with a matching socket in the pack.
2. Widens anything thinner than `min_feature` (the aerials are 0.4 mm at this
   scale).
3. Voxel-remeshes to one watertight solid, closing the open shells.
4. Shaves `foot_trim` off the soles so it stands flat — the game feet taper
   to near-points. The height scale compensates, so `--height` still lands.
5. Bores the keyring slot below the crown: a 4 mm bore stretched 1.7× downward.
   A round hole through a 16 mm helmet is a tunnel no split ring can curve
   through; a slot gives the ring room below the axis while keeping
   `keyring_margin` of solid helmet above it.
6. Splits the visor (faces using the `Player_Helm` material) into its own
   part, shrunk by `visor_gap` so it drops into the recess with room for glue.
7. Decimates coplanar triangles and triangulates before export, so the STL is
   a few MB rather than 20.

## Parts

| File | Colour | Size | Volume |
| --- | --- | --- | --- |
| `astronaut-body.stl` | white | 39.7 × 25.3 × 54.9 | 16.0 cm³ |
| `astronaut-visor.stl` | black | 25.3 × 20.6 × 10.6 | 1.1 cm³ |
| `astronaut-backpack.stl` | white | 19.4 × 31.2 × 13.5 | 2.9 cm³ |

The soles are two flat patches totalling ~93 mm², so it stands unaided and
sticks to the bed without a brim.

All three are single watertight solids sitting on Z = 0 in print orientation:
the body standing, the visor face-down, the backpack on its mating face with
the aerials running along the bed.

## Build

```bash
uv run --script models/astronaut/astronaut.py out/astronaut
```

Every part is checked after export: a part that is not a single watertight
solid fails the run. Marked `build: manual`, so `mise run build` and CI skip it — it needs Blender
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
| `--plump` / `--head-scale` | 1.18 / 1.1 | widen against height; helmet scale |
| `--foot-trim` | 1.0 | mm shaved off the soles |
| `--keyring-dia` / `--keyring-margin` | 4 / 3.5 | mm, bore and solid helmet above it |
| `--keyring-stretch` / `--keyring-cone` | 1.7 / 1 | slot stretch downward; mouth lead-in |
| `--split-pack` | 1 | 0 keeps the backpack on the body |
| `--boss` / `--boss-fit` | 6 2 2 / 0.2 | mm, locating cone base/tip/length, clearance |
| `--simplify-angle` | 2 | deg, coplanar merge limit |

## Print

- P1S, PLA, 0.2 mm layers, 4 walls, 20 % infill.
- Body: white, standing as exported. Tree supports under the arms only now
  that the backpack is its own part; keep them off the helmet front.
- Visor: black, face-down as exported, no supports.
- Backpack: white, flat as exported. The aerials run along the bed — much
  stronger than printing them upright — but hover ~5 mm up, so they need two
  small supports.
- Glue the visor into its recess and the backpack onto the locating cone with
  a dab of CA.
- The hole has ~99 mm² of solid helmet above it, which is far more than a
  keyring needs; the weak direction is layer adhesion, so 4 walls matter more
  than infill.
- The aerials are still the fragile part (1.6 mm), though printing them
  lying down helps. Raise `--min-feature` to 2–2.5 for a keyring that lives
  in a pocket.
- The keyring slot is 4 × 6.8 mm with a ~6 mm straight run, so a 20–30 mm
  split ring threads through with room to spare.

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

v1 printed at 55 mm: good, but the 3.5 mm round bore was a 16 mm tunnel no
keyring could curve through, the figure read too tall, and the upright
aerials were delicate. v2 answers all three: keyring slot, plumper
proportions with a bigger head, and the backpack split off to print flat.
v3 flattens the soles. Not yet printed.
