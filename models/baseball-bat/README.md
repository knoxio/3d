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

Print `knob_end-plate.3mf` first — the socket test piece and the cap on one
plate, the taller of them 25 mm — to settle the fit before committing to the
180 mm knob.

The pack, as measured by the owner: 131.4 mm long without its leads, up to
Ø20.5; a 70 mm charging lead with a 2S balance connector and a 65 mm power lead
with a JST, which may be cut and replaced. Whether the leads leave the end
straight or from the side is not yet known.

Still to do: the sleeve that guides the pack, and merging the new knob end onto
the knob's mesh.

## Assumptions

The knob's outline — Ø40 handle, Ø50 knob, 5 mm chamfers, 25 mm tall, Ø35 bore —
is read off the mesh, not measured on a print. The pack's Ø20.5 is the owner's
figure.

## Status

draft — rescaled to 100 % and sliced, not printed. The battery door's lock is
designed and awaiting a test print; the pack sleeve and the merged knob are not
done.
