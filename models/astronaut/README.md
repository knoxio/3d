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
   the back — the plane is set just under the 5th percentile of the back
   surface inside the footprint, so shaving flattens nearly all of it rather
   than clipping a few high spots — the pack cut off flat
   to match with `boss_fit` of glue gap, and two locating cones on the pad
   with sockets in the pack. Each boss is a shank buried in the torso plus
   the cone that stands proud, so its size at the pad does not change with
   how deep the shank reaches. A pack moulded to the torso has a hollow in its face
   that prints badly, and the cut also takes the aerials' forward lean off,
   so the whole part lies down on the bed.
5. Shaves `foot_trim` off the soles so it stands flat — the game feet taper
   to near-points. The height scale compensates, so `--height` still lands.
6. Bores the keyring hole below the crown. Size it by the ring's **wire**,
   not its diameter: a split ring threads as two coils lying side by side, so
   the hole needs about twice the wire thickness whichever way the ring ends
   up sitting — 6 mm round for 2.5 mm wire (a 20 mm ID / 25 mm OD ring).
   Placement is worked out rather than given: the hole is pushed back until it
   clears the visor plug, which runs the full height of the helmet's face, and
   `keyring_margin` is measured from the helmet's surface **directly above the
   hole**, not from the crown — the dome falls away behind the crown, and a
   hole set from the crown's height breaks out through the top.
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
| `astronaut-body.stl` | white | 36.3 × 19.6 × 49.9 | 10.6 cm³ |
| `astronaut-visor.stl` | black | 22.0 × 20.9 × 10.1 | 1.7 cm³ |
| `astronaut-backpack.stl` | white | 17.8 × 25.9 × 10.3 | 1.6 cm³ |
| `astronaut-visor-facets.stl` | black | 84.6 × 14.0 × 7.9 | 1.7 cm³ |

The soles are two flat patches totalling ~93 mm², so it stands unaided and
sticks to the bed without a brim.

All three sit on Z = 0 in print orientation and are closed solids.
Orientation:
the body standing, the visor face-down, the backpack on its mating face with
the aerials running along the bed.

## Build

```bash
uv run --script models/astronaut/astronaut.py out/astronaut
```

The joint is checked in the assembled position before anything is exported:
the pack must not foul the torso, each cone must be solid on the body, and
the pack must be hollow exactly where that cone sits. Each caught a real
defect — cones half floating where the torso fell away behind the pad, and
the pack held off the torso by unshaved strips at the pad's edges.

Every part is then checked after export: each shell must be closed and the
main one must hold at least 95 % of the volume. Shells that overlap the part
are kept (a slicer unions them); shells that touch nothing are dropped as
debris — the wider pad shave shears two small corners off the arm roots. Marked `build: manual`, so `mise run build` and CI skip it — it needs Blender
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
| `--keyring-slot` | 6 6 | mm, hole front-to-back and vertically |
| `--keyring-margin` | 1.5 | mm of helmet above the hole, from the local surface |
| `--keyring-back` | 1 | mm further back, on top of the visor clearance |
| `--keyring-cone` | 0 | mm, mouth funnel; 0 leaves a plain tube |
| `--pad-depth` | 2 | mm the backpack pad is sunk into the torso |
| `--assembly` | 0 | 1 also writes `assembly-preview.stl`, for looking at, not printing |
| `--visor-facets` / `--facet-gap` | 1 / 3 | split the visor into facets; mm between them |
| `--boss-count` | 2 | locating cones on the pad |
| `--split-pack` | 1 | 0 keeps the backpack on the body |
| `--boss` / `--boss-fit` | 6 2 2 / 0.2 | mm, locating cone base/tip/length, clearance |
| `--simplify-angle` | 2 | deg, coplanar merge limit |

## Visor facets

`astronaut-visor-facets.stl` is the same visor cut into its five facets, each
turned so its facet lies on the bed — for printing against a textured or
holographic plate and seeing how the pattern reads on each angle. The five
pieces sit in a row `facet_gap` apart, roughly 79 mm² of contact each, and
together they hold the same volume as the whole plug, so the cuts tile it
exactly. Glue them back into the helmet recess as one, or print the plain
`astronaut-visor.stl` instead. `--visor-facets 0` skips the file.

## Keyring hole

6 mm round and a plain tube — funnelled mouths left a visible step around the
opening. 1.4 mm of helmet above it, walls 3.0 mm at the front and 2.4 mm at
the back, through a 12–15 mm bore. A 20 mm ID / 25 mm OD ring (2.5 mm wire)
needs 5.0 mm for its two coils and, at the longest bore, 5.4 mm once its
curve is allowed for — against 5.8 mm of hole.

Nothing may take material out of the visor plug, since those are already
printed: the build intersects each cutting solid with the plug and fails if
the overlap is more than 0.1 mm³. The plug is the pocket intersected with the
helmet, not the pocket prism, which reaches far out into the air in front of
the face where cutting costs nothing.

## Checking the fit

`--assembly 1` writes `assembly-preview.stl`: the body and backpack as they
sit together. It is not printable — it is there to look at.

The pad ends up flat within ~0.4 mm, and the pegs stand ~4 mm proud of it
(the cone plus however much shank the torso's curve exposes). The pack's
sockets are cut from the same solids, so they match whatever is exposed.

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

Archived: fully printed. Print feedback drove v2–v8 — keyring sizing, proportions, flat soles, sharp armpits, the flat visor
pocket, the flat backpack pad with two locating cones, and a plain 6 mm
keyring tube.

All three parts are printed, including the v8.5 body with the plain 6 mm
keyring tube: 5.8 mm bore, 1.4 mm of helmet above it, walls 3.0 mm front and
2.4 mm back, sized for a 20 mm ID / 25 mm OD ring whose two coils need
5.0 mm. Whether that ring threads easily in the hand is not recorded here.

Open, and not a model problem: the facet plate printed on a holographic film
came out with holes in the first layer, at the centre of each triangle and
patchily elsewhere. The facet bottoms measure flat — 92 % of the triangle in
contact within 0.01 mm of the bed, 0.007 mm at the centre — so this is first
layer adhesion on the film, with a 0.1 mm initial layer leaving no margin for
its waviness. Suggested there: initial layer 0.15–0.16 mm, fan off for the
first layers, a little more flow, glue stick.

## Head-only QR variant

`head_qr.py` produces the helmet only, with the visor opening on the bed,
a perpendicular flat neck cut, and the successful **15 mm square-module QR**
on a shaved rear face opposite the visor. The black pattern stays about 12.1 mm
across and 0.2 mm high. Only the black artwork needs a flat seat: the four-module
white quiet zone continues over the surrounding curved helmet, without a
separate flat border. This retains 1.2 mm more helmet depth than the first
head version. The 15 mm dimension includes that curved white quiet zone.

The existing body STL is the dimensional reference. It is never scaled.
The latest body rebuilt with `--keyring-back 0` supplies only a bounded crown
region behind the visor; the original visor pocket is retained. The hole moves
1.00 mm toward the visor and 0.37 mm upward, with its measured 5.99 mm diameter
unchanged within 0.008 mm. The rest of the current body pipeline and its
standard keyring defaults are unchanged.

```sh
uv run --script models/astronaut/astronaut.py tmp/astronaut-head/forward-source --keyring-back 0
uv run --script models/astronaut/head_qr.py out/astronaut-head-qr \
  --body /absolute/path/to/current/astronaut-body.stl \
  --forward-body tmp/astronaut-head/forward-source/astronaut-body.stl \
  --svg /absolute/path/to/square-qr.svg
```

This variant is calibrated to the current 50 mm astronaut, not an arbitrary
resized input. Mismatched body bounds, a changed bore diameter, a missing
visor plane, unsupported black artwork, or a quiet zone outside the helmet
outline causes the build to fail.
The source SVG uses a 33-module QR with 14 SVG units per module.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `HEAD_DEPTH` | 14.0 mm | White helmet depth in print orientation |
| `QR_SIZE` / `QR_HEIGHT` | 15 / 0.2 mm | Quiet-zone square and black relief |
| `SHOULDER_CUT_Y` | −28 mm | Restrict shoulder removal to the neck end |
| `ENVELOPE_ALLOWANCE` | 0.15 mm | Preserve voxel-rounded lower helmet facets |
| `NECK_Y` | −24.5 mm | Neck cut in the untranslated visor-down frame |
| `HEAD_X` | −12.230462, 12.042460 mm | Original helmet width; clips collar wings |
| `QR_CENTRE_X` / `QR_CENTRE_Y` | −0.06 / −36.47 mm | QR placement in that frame |
| `QR_STL_GAP` | 0.001 mm | Sub-print-resolution separation of diagonal QR contacts for closed STL export |

The shoulders are trimmed along the existing lower helmet facets, extended
with a 0.15 mm outward allowance. These trims apply only beyond print Y=−28 mm.
The visible neck ends in a perpendicular cut, retaining about 1.6 mm below
the recess. The moved bore leaves
about 1.88 mm toward the visor and 3.12 mm toward the QR face at its centre;
the geometry report deducts 0.1 mm from each as a conservative allowance for
the slightly tilted bore. The front wall remains below the general 2 mm
load-bearing target to keep the current visor and six-millimetre hole. The
existing approximately 1.4 mm crown roof
is retained. Do not enlarge the bore or deepen the QR shave.

The white STL is one closed solid, about 24.27 × 23.69 × 14 mm. The black
part raises overall depth to 14.2 mm. Float32 STL round trips are checked;
zero-volume triangles collapsed by quantization are discarded and tiny
triangle/quad openings are repaired only within a 0.001 mm³ volume-change limit. Black
and white share an origin: import both STLs together as one multipart object,
or open the generated material-assigned 3MF. Filament 1 is black, 2 is white.

Print with the P1S **0.2 mm nozzle**, AMS, 0.10 mm layers, 0.22 mm lines,
4 walls, 20% gyroid, 6 top and 5 bottom layers. Use normal snug supports from
the bed inside the downward-facing visor recess (its ceiling spans about
21 mm), a 3 mm outer brim, and a prime tower. The local sliced project uses
white support with 0.15 mm top separation and 0.25 mm interface spacing.
Remove the supports and brim carefully before fitting an existing visor.
Smooth PEI is selected in the supplied project; select the actual plate and
map black/white to the loaded AMS slots. White prints first, then only the
two black QR layers. Do not independently arrange or scale the two parts.

The shallower sliced head estimates **1 h 31 min 16 s / 5.09 g**, including
supports, brim and purge.

The build writes a three-view PNG and geometry report beside the printable
files. Status: geometry checked and sliced; physical fit, support release and
QR scan reliability still need the first head print.
