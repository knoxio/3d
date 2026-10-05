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
| Buttons | X 60.5, Y 8.4 / 16.2 / 24.0, Ø6 | derived; gaps disagree by ~1.4, holes are Ø7.5 |
| Encoder shaft | X 78.2, Y 13.2 | four readings closing within 0.35 |
| Screen PCB | corner at 0.1, 3.5 | rough; overhangs the back edge by 7 |

## Two lids

The elbow lid carries the screen and comes off for reset and boot; the hand
lid covers buttons and knob and stays shut. Splitting at X 46 means the elbow
lid opens without disturbing the knob.

The screen is **not** fixed to the perfboard — it floats on wires, so it
mounts to the elbow lid on four bosses at its own Ø3.5 holes, and the window
is cut relative to those, not to the green board.

The knob opening is Ø17 clearance around the Ø14.5 knob, with no hole for the
bush: the bush top sits 11 mm above the board, below the lid's inner face, so
nothing has to line up with it.

## Strap

The band crosses the arm, so the lugs are on the long sides, not the ends. Each
is a tall plate standing `strap_gap` off the flank on a post at either end: the
band threads up the gap behind it, open top and bottom, and covers the case's
height on the way up. Lugs at the ends would run the band along the arm.

## Battery

Outside the case, under the band, so it can be swapped mid-event. A wire
leaves through the floor near the elbow end to a JST connector. No charger,
no power switch inside.

## Known loose ends

- `forearm_r` 40 mm is a guess; the underside curve needs the real forearm.
- Wire space under the board is 5.5 mm, which the build was measured down to.
- `usb_y` 15 is a guess — the socket's position across the board is unmeasured.
- Screen position is rough (±1 mm), which is why the window has 0.8 mm margin
  and the lit area is derived rather than measured directly.
- The on-screen C/B/A labels will not line up with the buttons: the screen
  sits ~7 mm further back than the button column. That is a firmware offset.

## Build

```bash
mise run build wrist-controller
```

## Status

draft — nothing printed. Case is 101.5 × 43.1 × 24.5 mm. Shell, lids, bosses,
openings and strap lugs; no lip seal or edge rounding yet.
