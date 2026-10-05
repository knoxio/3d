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
| Board holes | Ø2.5 at 2.45 in from both green edges; Ø3.5 at X 85.75, Y 6.95/23.05 | derived from edge gaps |
| Buttons | X 60.5, Y 8.4 / 16.2 / 24.0, Ø6 | derived; gaps disagree by ~1.4, holes are Ø7.0 |
| Encoder shaft | X 78.2, Y 13.2 | four readings closing within 0.35 |
| Screen PCB | corner at 0.1, 3.5 | rough; overhangs the back edge by 7 |
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

Its glass sits straight against the roof's inner face — that face is the datum,
not a boss. Four Ø3.2 pins pass through the mounting holes and stand 1.5 mm
proud of the PCB; flatten them with a hot iron. A blob of hot glue instead
works just as well, and the pins still locate it. The case's own lid screws are
unchanged: M2 into heat-set inserts.

The knob opening clears the **bush**, not the knob: Ø8.0 around the Ø6.85
thread. The knob itself stays off until the lid is on, and its Ø14.5 skirt then
hides the hole — asserted, along with the 0.5 mm between the lid's top face and
the knob's underside at 11 mm.

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
- Screen position is rough (±1 mm), which is why the window has 0.8 mm margin
  and the lit area is derived rather than measured directly.
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
