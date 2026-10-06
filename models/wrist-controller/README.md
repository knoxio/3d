# Wrist controller enclosure

Case for a wrist-worn costume remote, built around an **existing perfboard
build** rather than loose modules: a 70 × 30 green perfboard carrying the
ESP32-S3, three buttons and an MPU-6050, with a KY-040 encoder board butted
against its hand end, and a 1.3" OLED floating on wires above.

Everything is in one frame: **origin at the green board's corner at the elbow
end, front edge, on the board's top face.** X toward the hand, Y across the
arm, Z up. Measurements off the bench go straight into the parameter block.

## Layout

| Feature | Position | From |
| --- | --- | --- |
| Green board | 70 × 30 × 1.5 at origin | measured |
| KY-040 board | 18.5 × 25.6, butted with 0.5 gap | measured |
| Board holes | green Ø2.5 at a 65.5 × 25.9 pitch; Ø3.5 at X 86.25, Y 6.95/23.05 | green pitch measured; KY-040 from edge gaps |
| Buttons | X 60.5, Y 8.4 / 16.2 / 24.0, Ø6 | derived; gaps disagree by ~1.4, holes are Ø7.0 |
| Encoder shaft | X 78.2, Y 13.2 | four readings closing within 0.35 |
| Screen PCB | corner at 0.1, 3.5 | rough; overhangs the back edge by 7 |
| Screen holes | 2.55 in from both sides, 2.25 front, 3.25 back → 30.4 × 28.0 pitch | measured edge gaps + half the Ø3.5 hole |
| USB-C | centre Y 18.0 | 7.5 gap to the board's back edge, Ø9 socket assumed |

## Flat base, raised screen lid

The base is one height all round: its rim stops at `hand_top` 8.5 above the
board, which is all the knob half needs, because buttons and knob are meant to
stand proud of it — the button bodies pass through Ø7.0 holes and the encoder's
bush through a Ø8.0 one.

The extra height the screen wants belongs to its lid instead. The elbow lid is
a raised cap: a flange that lands on the base's rim, walls, and a roof 13.5 mm
above the board with the window in it. Its hand end ramps down to the flange at
45°, so it prints without support and meets the flat hand lid flush. Case:
**24.5 mm over the screen, 19.5 mm over the knob.**

It lands on the base's rim at four screw tabs rather than a continuous flange.
A flange would be a 6 mm ledge running right round the inside of the cap, and
printed roof-down that is a long unsupported overhang. It also had to be cut
away for the ESP, the MPU and the screen anyway.

## Two lids

The elbow lid carries the screen and comes off for reset and boot; the hand
lid covers buttons and knob and stays shut. Splitting at X 46 means the elbow
lid opens without disturbing the knob.

The screen is **not** fixed to the perfboard — it floats on wires, so it
mounts to the elbow lid at its own Ø3.5 holes, and the window is cut relative
to those, not to the green board.

The screen, front to back across its 33.5 mm PCB, as measured:

| From the PCB's front edge | What |
| --- | --- |
| 0 – 4.5 | bare board |
| 4.5 – 8.3 | the lip: thin glass over the flex, 3.8 wide |
| 8.3 – 26.9 | the glass, 18.6 |
| 10.6 – 25.3 | lit rows — the first is 6.1 in from the lip's outer edge |
| 26.9 – 33.5 | bare board, with the back pair of holes |

The lip is a strip in front of the 18.6 mm glass, not part of it, and it faces
the front of the case. Across, the 29.42 mm lit area is centred in the 34.5 mm
glass. Lit size is the 1.3" 128 × 64 panel's active area, 29.42 × 14.7.

The window is that lit area plus 1 mm of unlit glass all round: **31.4 × 16.7**.
It stays on the glass, 1.3 mm short of the lip and 0.6 mm short of the back
edge, so neither the flex nor the board can show.

Three earlier prints each got this wrong a different way, and this one geometry
accounts for all three to within a few tenths:

| Print | Window, front to back | Geometry predicts | Seen |
| --- | --- | --- | --- |
| 1 | 15.2 – 30.0 | front rows cropped 0.6, 0.7 dark at the back; 2.4 empty at one side | "bottom ones gone, 1.1 on top, 2.5 empty to the side" |
| 2 | 8.4 – 26.2 | 3.4 of lip showing in front, back rows cropped 2.6 | flex inside the window, top rows missing |
| 3 | 14.3 – 32.1 | pixels at the front edge, 1.7 of bare board at the back | exactly that, with both back holes in view |

The mistakes behind them: treating the lip as part of the 18.6 mm glass, then
cutting the window to "the glass" starting at the lip's edge, then deciding the
lip faced the back. Two asserts now state what a window must do — contain the
lit area, stay on the glass — and the assembly preview draws the PCB, lip,
glass and lit area, so a render shows the pixels in the opening.

**PURGE** is sunk 0.4 mm into the face below the window — two layers, not
raised, because that face prints against the bed. The letters therefore start
a couple of layers up: swap filament at layer 3 and they come out in their own
colour, with the rest of the lid in the second colour and only its top face in
the first.

Outside, it flares at 45° to **33.8 × 19.1**. The roof is 2 mm of plastic
standing in front of the glass, which costs the display its viewing angle at
the edges; the bevel takes 1.2 of those 2 mm back and leaves 0.8 mm of straight
wall at the seat. Printed roof-down the flare is a 45° face, so it still needs
no support.

Its glass sits straight against the roof's inner face — that face is the datum,
not a boss. Four Ø3.2 pins pass through the mounting holes and stand 1.5 mm
proud of the PCB; flatten them with a hot iron. A blob of hot glue instead
works just as well, and the pins still locate it. The case's own lid screws are
unchanged: M2 into heat-set inserts.

The knob opening clears the **bush**, not the knob: Ø8.0 around the Ø6.85
thread. The knob itself stays off until the lid is on, and its Ø14.5 skirt then
hides the hole — asserted, along with the 0.5 mm between the lid's top face and
the knob's underside at 11 mm.

## Board posts

Every post in the case is the same Ø6 boss with a Ø3.2 insert pilot — the
board's hole diameter is not used anywhere, and does not need to be. What it
does decide is how accurate the post has to be:

| Board | Hole | Play on an M2 screw | Pitch may be out by |
| --- | --- | --- | --- |
| Green perfboard | Ø2.5 | 0.25 mm a side | 0.5 mm |
| KY-040 | Ø3.5 | 0.75 mm a side | 1.5 mm |

So the green board's pitch has to be right to half a millimetre. It was taken
from a reported "~1.2 mm from the edge", giving 65.1 × 25.1; measured, it is
**65.5 × 25.9**. Across the arm that is 0.8 mm out — more than the Ø2.5 holes
can absorb, which is why all four screws pulled.

Hole centres are now derived from the gap to the board's edge rather than
written out as numbers. A literal is how the KY-040's centre came to be 0.5 mm
out — it had been worked out without the 0.5 mm gap between the two boards.

## Lid fixings

The boards go into the case from above, so a post anywhere inside their
footprint blocks them at every height — tapering its foot does not help. The
posts sit against the outer wall instead, half buried in it, in the four places
the boards leave free:

| Where | Why it is free |
| --- | --- |
| Off both ends | the boards stop 5 and 3.5 mm short |
| Along the back | 7.5 mm of clearance for the screen's overhang |
| Front, over the KY-040 | that board is 25.6 wide against the green one's 30 |
| Front, elsewhere | **nothing fits** — only 2.6 mm |

That leaves the seam's front corner with no room for an insert's Ø6 boss. It
gets a Ø4 one the screw taps for itself, which clears the board by 0.6 mm. The
other seven are M2 heat-set inserts as before.

The cap meets those posts at four Ø7.5 tabs. They were Ø10, which reached far
enough inboard for one of them to swallow a screen pin and to sit under the
PCB's corner — a tab's top face and the PCB's underside are both at 10.5 mm, so
anything on the back of the board would have been pressed.

Three asserts hold all of this: no post inside a board's footprint, no tab
within reach of a screen pin, no tab under the screen. Each was checked to fail
when the geometry is moved to break it.

## Strap

The band crosses the arm, so the lugs are on the long sides, not the ends. Each
is a tall plate standing `strap_gap` off the flank on a post at either end: the
band threads up the gap behind it, open top and bottom, and covers the case's
height on the way up. Lugs at the ends would run the band along the arm.

The opening is 52 mm, far wider than the 24 mm band, so the pull is spread
along the flank rather than concentrated on two short posts. The plate runs
down to the plane the case stands on, so it prints off the bed instead of
cantilevering off its posts, and the band cannot slip out underneath.

## Battery

Outside the case, under the band, so it can be swapped mid-event. Two wires
leave through a Ø3 hole in the floor at the front elbow corner — out of the
band's way, and clear of both the corner post and the board's boss. No
charger, no power switch inside.

## Known loose ends

- Wire space under the board is 5.5 mm, which the build was measured down to.
- The USB-C socket's *width* is assumed at 9 mm; its position comes from the
  measured 7.5 mm gap to the board's back edge. The opening is 13 mm wide, so
  the assumption has ~2 mm of slack each side.
- The lit area's size, 29.42 × 14.7, is the panel's datasheet figure rather
  than a measurement. Its position is measured. The 1 mm margin covers both.
- The screen's rough position (±1 mm) no longer affects the window: the window
  and the staking pins are both derived from the same four mounting holes.
- The on-screen C/B/A labels will not line up with the buttons: the screen
  sits ~7 mm further back than the button column. That is a firmware offset.

## Print

Open `out/wrist-controller/wrist_controller-plate.3mf` — all three pieces on
one 107.5 × 109.2 mm patch of bed, each already in the orientation it prints
in. PLA, 0.2 mm layers, 3 walls, 20% infill.

Supports: **none.** The elbow lid prints roof-down and the only overhangs left
are its four screw tabs — a Ø10 disc each, two layers thick, at the very top of
the walls. They print over air with a little droop and no support; paint
support onto those four spots if the seat matters more than the time. The base
prints flat-bottomed and the strap lugs reach the bed.

```bash
mise run build wrist-controller
```

## Status

draft — nothing printed. Case is 101.5 × 44.1, 19.5 mm tall with the screen
cap rising to 24.5 mm, flat underside. Shell, lids, bosses, openings and strap
lugs; no lip seal or edge rounding yet.
