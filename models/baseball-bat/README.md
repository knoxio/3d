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

## Assumptions

None about fit yet — nothing has been changed but scale and placement.

## Status

draft — rescaled to 100 % and sliced, not printed. An opening for swapping
batteries is still to be designed.
