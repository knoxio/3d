# Baseball bat

A five-piece hollow bat with a honeycomb barrel, to be lit from inside and
carry its own batteries. Someone else's model, rescaled and re-plated here.

**Source:** "Fun Baseball bat – Small printer compatible" by Vulcain, MakerWorld,
CC BY-NC. Download the project as `V2A1MiniCompatible.3mf` into this directory.
It is not committed, and neither is anything built from it.

## Parts

Handle to tip, at the designer's size (100 %). Every piece is a watertight
single body with a 2.5 mm wall.

| Part | Project name | Size | Notes |
| --- | --- | --- | --- |
| knob | `stl_3` | Ø50 × 180 | open at the bottom: a Ø26.8 hole into a Ø35 bore |
| handle | `stl_1` | Ø40 × 180 | plain tube, bore Ø35 |
| taper | `stl_4` | Ø68.9 × 180 | honeycomb in its upper half |
| barrel | `stl_5` | Ø78.6 × 180 | honeycomb, bore Ø73.5 |
| tip | `stl_2` | Ø78.6 × 150 | honeycomb, domed; stored flipped, so it prints dome-down |

Assembled it is 831 mm. Each joint is a 9.75 mm spigot into the next part's
bore at a line-to-line fit, meant to be glued. The narrowest way through each
joint, handle to tip, is Ø30.6, Ø31.4, Ø59.7 and Ø69.1.

## Parameters

| Option | Default | Meaning |
| --- | --- | --- |
| `--scale` | 1.0 | 1.0 is the designer's size; the download was saved at 0.72 |
| `--src` | `V2A1MiniCompatible.3mf` here | the downloaded project |

The plate is laid out by the script; it stops if a part would be taller than
245 mm or the five do not fit one 256 mm plate. 1.36 is the most the P1S takes.

## Build

```bash
uv run --script models/baseball-bat/bat.py out/baseball-bat
```

## Print

`out/baseball-bat/bat-p1s.3mf`, with the project's own settings: PLA, 0.28 mm
layers, 2 walls, 10 % infill, 5 mm outer brim, no supports. Sliced by Bambu
Studio's CLI at 100 %: nothing outside the plate, 8 h 53 min, 320 g.

## Battery door

Two 18650s inline, as a wrapped pack up to Ø20.5 with its leads at one end, go
in through the knob. The cap carries no bending load there, and all four body
joints stay glued.

The original knob is a hollow cone behind a Ø26.4 hole, with nothing square to
latch on, so `knob_end.scad` replaces its bottom 25 mm: same silhouette
outside, a Ø35 socket inside, and a cap that forms the lower chamfer. The lock
is a three-start part-turn thread — three lugs through three notches, then
about 55° clockwise until the cap pulls up tight on its flange. Both bearing
faces are 45° cones on one helix, so they bear over their whole area, centre
the cap, and print without support. Print tolerance only moves the angle at
which it tightens: up to 22° later if the parts print 0.8 mm loose, 12° earlier
if they print 0.4 mm tight.

Checked by intersecting the two parts at sixteen positions: free on the way in
and while turning, touching on both faces when seated, solid contact if pulled
out or turned past tight.

### The pack and its sleeve

The pack, as measured by the owner: 2 × 18650 inline, shrink-wrapped, 131.4 mm
long and up to Ø20.5. Both leads leave one end straight out, at its edge: a
65 mm power lead with a 2-pin JST (which may be cut and replaced) and a 70 mm
charging lead with a 2S balance plug.

`sleeve` is a Ø24.5 tube for the pack with a Ø34.4 bay under it and a guide
ring above, sliding in the handle's Ø35 bore. It is not a carrier to be pulled
out: with the cap off, the pack slides out of it on its own.

- **Swung**, the pack is thrown toward the tip. The sleeve's closed top takes
  that, and its guide ring lands on the 45° shoulder inside the first joint.
  The cap carries none of it.
- **At rest**, a post up the middle of the cap holds the pack off its own
  leads. The leads leave the edge of the pack's end, so a central post misses
  them at whatever angle the cap stops.
- **The bay** under the pack, 45 mm plus the cap's hollow, takes both leads
  folded and the mated connectors. The bat's own lead comes down a slot beside
  the sleeve into it, and should be long enough to hang about 3 cm out of the
  knob so the plugs can be joined outside.
- The pack sits 64 to 196 mm from the bottom of the bat, so the sleeve's nose
  passes through the first joint into the handle piece.

Checked against the real bore read from the downloaded meshes: 0.28 mm of
clearance all the way up when resting on the cap, zero at the shoulder when
lifted the 0.5 mm of float, and blocked beyond that; clear of the socket and
the cap. It is 187 mm tall and about 38 g, and prints standing with no support.

### Printing

`knob_end-plate.3mf` has the socket test piece, the cap and the sleeve. The
socket and cap prove the lock. Cap, sleeve and pack stacked on the bench prove
the pack's fit and the post's length. The sleeve's fit in the handle cannot be
tried until the knob itself is printed.

Still to do: merging the new knob end onto the knob's mesh, and the full
project with every part.

## Assumptions

The knob's outline — Ø40 handle, Ø50 knob, 5 mm chamfers, 25 mm tall, Ø35 bore —
and the shoulder inside the first joint are read off the mesh, not measured on
a print. The pack's size is the owner's. The connectors' sizes are not
measured; the bay is sized generously rather than to them.

## Status

draft — rescaled to 100 % and sliced, not printed. The battery door's lock, cap
and pack sleeve are designed and awaiting a test print; the merged knob is not
done.
