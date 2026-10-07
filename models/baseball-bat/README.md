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
| `--no-door` | off | leave the knob as downloaded; required at any other scale |
| `--src` | `V2A1MiniCompatible.3mf` here | the downloaded project |

The plate is laid out by the script; it stops if a part would be taller than
245 mm or the five do not fit one 256 mm plate. 1.36 is the most the P1S takes.

## Build

```bash
uv run --script models/baseball-bat/bat.py out/baseball-bat
```

## Print

| Plate | Weight | Notes |
| --- | --- | --- |
| `bat-p1s.3mf` | 363 g | 9 h 47 min, sliced; the bat itself |
| `light-plate.3mf` | 86 g | natural for the tube, white for the rest; never black |
| `nail-nails.3mf` | 23 g | 24 nails, about 1 g each |

`out/baseball-bat/bat-p1s.3mf` is the whole bat on one plate: the four
unchanged pieces, the knob with its new end, the battery cap and the sleeve.
The project's own settings: PLA, 0.28 mm layers, 2 walls, 10 % infill, 5 mm
outer brim, no supports. Sliced by Bambu Studio's CLI: all seven parts
manifold, nothing outside the plate, 9 h 47 min, 363 g.

The plate picture stored inside the file is the download's and shows the old
layout until Bambu Studio saves it again.

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

### The merged knob

`bat.py` extracts the knob's mesh, has OpenSCAD cut it at 25 mm and join the new
end on, and writes the result back into the project in place of the original.
The knob is then 175 mm tall and stands on the plane where the cap meets it; the
cap is the other 5 mm, so the bat is still 831 mm.

Compared with its two sources: above the join it matches the downloaded knob to
0.000 mm, bore included, so the sleeve's check against that bore still holds;
below it, it matches the socket test piece that was printed, to 0.001 mm.

## Nails

The hexagons are a straight prism through the shell, the same from bore to
outside: **8.47 across the flats, 9.40 across the corners, in a 2.54 wall**.
There are 16 to a row, every 22.4°, with rows staggered 8.0 mm apart, so 16 mm
between rows that line up — about 300 on the barrel and as many again on the
tip. Measured by rasterising the wall from five radii, which agreed to 0.02 mm.

`nail.scad` is a spike on a flared head with a plug that pushes into a hexagon.

- The plug is **round, not hexagonal**, sized to the flats so it bears on all
  six. With twenty of these to push home, not having to clock each one is worth
  more than the corner contact.
- The head is a **45° cone, not a disc**. A disc would have to be dished to sit
  on a Ø78.6 shell, and printed plug-down its rim would be a 2.4 mm overhang on
  the very face that has to seat. A cone seats on its inner edge whatever the
  curvature, prints unsupported, and reads as a stud.
- It prints as modelled: plug on the bed, spike up, no supports.

### Fit, as printed

The first ladder (`nail-test.3mf`, plugs Ø8.5 to Ø7.5) put **Ø8.50 tight and
Ø8.30 snug**, so the hexagon prints close to its drawn 8.47 and the plug wants
to be **Ø8.40**.

Its two barbed pieces held only haphazardly, and the geometry says why: the
lip's widest point sat 2.39 mm below the head, inside a 2.54 mm wall. The barb
never cleared the back face, so anything that held was friction. The plug's
depth is now worked out from where the **catch** has to land —
`shell_wall + behind + lip_h` — which puts it 3.54 mm down, a millimetre clear
of the wall.

The second ladder settled it: **Ø8.40 goes in without strain, Ø8.45 not at
all**, and both hexagonal plugs fitted well. The printed hexagons are slightly
squashed, which is the argument against the hexagonal plug — it cannot rotate
to take up a hole that is out of shape, where a round one does not care.

So the nail is a **round Ø8.35 plug with the barb**, and it is the barb that
holds, not the fit. `nail-nails.3mf` is a batch of 24; `count` sets it.

## Light core

Three runs of 60/m WS2812B at 120° on a triangular spine, inside a thin printed
tube. The spine puts the strips about 5 mm off the axis and the tube's wall is
**26 mm** further out, so a 16.7 mm LED pitch has more than its own spacing in
which to blend. That distance, not LED density, is what makes the hexagons glow
rather than show dots — which is why 60/m is enough and 144/m would only cost
runtime.

The spine's faces are **16 mm** for a 10 mm strip. The extra margin is there
because the strip was bought but not in hand when this was drawn, and a face
that takes a 12 mm strip costs nothing.

**The core is shorter than the lit section**, because the bore is only Ø73.5 in
the middle of each part and the spiders have to reach it:

| | Bore | Core |
| --- | --- | --- |
| Barrel foot | Ø63.8, thickening into the taper | — |
| Barrel middle | Ø73.5 over z 35–161 | 126 mm |
| Barrel head | Ø69.1, the socket the tip sits on | — |
| Tip, first 17 mm | the dome | — |
| Tip | Ø73.5 over z 17–139 | 122 mm |

So 248 mm lit, 45 LEDs: 2.7 A all white, about a fifth of that in use, so
roughly 3 hours on the 2S 3000 mAh pack. The hexagons past each end of the core
catch spill from the open ends of the tube rather than going black.

Four pieces per lit section — a spine, a diffuser tube and a spider at each end.
The spiders are separate because they have to reach the bat's bore to centre
everything, and nothing that wide can pass down the tube: the tube slides onto
the spine, then the spiders cap it. Their webs are in two tiers, out to the bore
for the first 6 mm and then pulled back inside the collar.

The diffuser is Ø66, which clears a barbed nail standing 2.4 mm proud inside the
bore by 1.35 mm.

**It cannot go in after the bat is built.** The passages through the handle
joints are Ø30.6, so the core and diffuser are installed as the barrel and tip
are glued, and the battery lead comes up the spine from the knob.

### Getting light out

The shell is **50% open** — 59 mm² a hexagon, sixteen to a row, rows every
8 mm — so the holes are not the bottleneck. Two things are:

1. **What the tube is made of.** Natural or uncoloured PLA passes far more than
   white at the same thickness, and printed layers scatter plenty on their own.
   This is the largest single lever and it costs nothing. In black the tube is
   just something that blocks the light.
2. **How thick it is.** The wall is **0.6 mm** — one wide extrusion rather than
   two — with 0.9 mm bands over the first 10 mm at each end, where the collars
   grip and where it gets pushed. Every tenth of a millimetre in the middle is
   light that never leaves the bat; at the ends it is strength where a thin
   66 mm tube wants to go out of round.

The spine and spiders are better in **white**: they sit behind the LEDs, so
what they do is bounce light back out. Tube natural, innards white, if there is
a choice.

What cannot be fixed: roughly half the light leaving the tube lands on black
shell between the holes. Closing the 3.75 mm gap behind the shell would help a
little, but Ø68.5 is the most that clears a nail standing proud inside the bore,
and only the press-fit nail at that.

`light-plate.3mf` is the whole core on one bed: two tubes, two spines, four
spiders, 204 × 216 mm, 91 g. `light-sample.3mf` is 70 mm of the same, for
checking the glow against a real strip first where there is time for it.

## Assumptions

The knob's outline — Ø40 handle, Ø50 knob, 5 mm chamfers, 25 mm tall, Ø35 bore —
and the shoulder inside the first joint are read off the mesh, not measured on
a print. The pack's size is the owner's. The connectors' sizes are not
measured; the bay is sized generously rather than to them.

## Status

draft — the twist lock was test-printed and works; the nail fit ladder is
printed but not yet reported on. The whole bat, with the
merged knob, the cap and the sleeve, is built and sliced but not printed, so
the sleeve's fit in the handle and the pack's fit in the sleeve are unproven.
