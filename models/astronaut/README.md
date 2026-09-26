# Astronaut keyring

The Unspoken game's astronaut as a three-part printable keyring: white body,
black visor plug, and a separate backpack that prints lying down. Default
50 mm tall, with chunkier proportions than the game mesh so it reads as a
keyring rather than a shrunken character.

The source mesh is a rigged, low-poly game asset with open shells, so nothing
about it is printable as-is. `astronaut.py` drives Blender to fix that:

1. Swings the arms down from the T-pose (`arm_drop`, 35°). The swing is
   rigid, not skinned — the rig's smooth weights tear a 265-triangle
   shoulder apart. The faces bridging arm to torso are dragged along with it,
   which is what shapes the shoulder, but underneath they sag into a rounded
   web that makes the arm look pinched. Nothing is cut away — cutting leaves
   slots and holes at the back, where the arm genuinely stands off the torso.
   Instead the arm's own underside faces are extended `arm_insert` mm into
   the torso as a slab, filling the hollow, so the weld reads as a sharp
   armpit crease.
1. Reproportions it: the body widens (`plump`) and compresses vertically
   (`squash`), while the head scales **uniformly** (`head_scale`) about the
   neck and drops with it. Body and head are treated separately on purpose —
   widening the whole figure turns the helmet into a blob.
1. Splits the backpack off: the components sitting behind the torso, minus
   the hip pods, which are behind it but far off the centreline. The pack is
   then subtracted from an inflated copy of the body, so its front face
   conforms to the torso with a `boss_fit` gap, and a locating cone is added
   to the body with a matching socket in the pack.
2. Widens anything thinner than `min_feature` (the aerials are 0.4 mm at this
   scale).
3. Voxel-remeshes to one watertight solid, closing the open shells.
4. Flattens where the backpack meets the torso: a pad sunk `pad_depth` into
   the back, the pack cut off flat to match with `boss_fit` of glue gap, and
   two locating cones. A pack moulded to the torso has a hollow in its face
   that prints badly, and the cut also takes the aerials' forward lean off,
   so the whole part lies down on the bed.
5. Shaves `foot_trim` off the soles so it stands flat — the game feet taper
   to near-points. The height scale compensates, so `--height` still lands.
6. Bores the keyring slot below the crown: a 3.6 mm bore stretched 2× downward
   and funnelled at each mouth. A round hole through the helmet is a tunnel no
   split ring can curve through; the slot gives the ring room below the axis,
   and the funnels — dropped by their own radius so they open downward only —
   shorten the straight run without touching the `keyring_margin` of solid
   helmet above. The helmet narrows sharply toward the crown, so height is the
   main lever on bore length.
7. Splits the visor (faces using the `Player_Helm` material) into its own
   part, shrunk by `visor_gap` so it drops into the recess with room for glue.
   The pocket is a flat-backed prism, not a thickened copy of the visor faces:
   those form a shallow pyramid, and following it would leave a dished recess
   and a plug with no flat side to print on.
8. Decimates coplanar triangles and triangulates before export, so the STL is
   a few MB rather than 20.

The weld is a voxel remesh, which resamples every flat facet onto a grid and
leaves the silhouette edges stair-stepped by about half a voxel. At 0.12 mm
that is ±0.06 mm — well under a 0.4 mm nozzle and 0.2 mm layers, so it cannot
print, but it is visible in a slicer at high zoom. Finer voxels are
impractical: 0.08 mm takes over ten minutes, and each halving is ~8x the
work. Welding with exact booleans instead would keep the facets perfectly
flat, but the source has open shells (the collar among them) that will not
close, and boolean unions over them come out hollow.

## Parts

| File | Colour | Size | Volume |
| --- | --- | --- | --- |
| `astronaut-body.stl` | white | 36.3 × 19.6 × 49.9 | 10.9 cm³ |
| `astronaut-visor.stl` | black | 22.0 × 20.9 × 10.1 | 1.7 cm³ |
| `astronaut-backpack.stl` | white | 17.8 × 25.9 × 8.4 | 1.2 cm³ |

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
| `--height` | 50 | mm, overall height |
| `--arm-drop` / `--arm-insert` | 35 / 10 | deg of arm swing; mm the underside slab reaches into the torso |
| `--min-feature` | 1.6 | mm, thinnest part allowed |
| `--voxel` | 0.12 | mm, remesh resolution — and the size of the facet stair-stepping |
| `--visor-depth` / `--visor-gap` | 3 / 0.15 | mm, plug depth and glue clearance |
| `--plump` / `--squash` | 1.15 / 0.88 | body only: wider across, shorter |
| `--head-scale` | 1.2 | helmet, uniform about the neck |
| `--foot-trim` | 1.0 | mm shaved off the soles |
| `--keyring-dia` / `--keyring-margin` | 3.6 / 2 | mm, bore and solid helmet above it |
| `--keyring-back` | 1.5 | mm toward the rear of the helmet |
| `--keyring-stretch` / `--keyring-cone` | 2 / 3 | slot stretch downward; mouth funnel |
| `--pad-depth` | 2 | mm the backpack pad is sunk into the torso |
| `--boss-count` | 2 | locating cones on the pad |
| `--split-pack` | 1 | 0 keeps the backpack on the body |
| `--boss` / `--boss-fit` | 6 2 2 / 0.2 | mm, locating cone base/tip/length, clearance |
| `--simplify-angle` | 2 | deg, coplanar merge limit |

## Print

- P1S, PLA, 0.2 mm layers, 4 walls, 20 % infill.
- Body: white, standing as exported. Tree supports under the arms only now
  that the backpack is its own part; keep them off the helmet front.
- Visor: black, face-down as exported, no supports.
- Backpack: white, flat as exported, **no supports**. Its mating face is flat
  and lies on the bed with ~229 mm² of contact, and the aerials — trimmed
  flush with that face — rest on the bed too, so they print along their
  length, which is far stronger than standing them up.
- Visor: the plug is a flat slab, so it lies flat on the bed.
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
v3 flattens the soles. v4 shrinks it to 50 mm and
fixes the helmet, which v2 had squashed by widening the whole figure: body
and head are now reproportioned separately. Not yet printed.
