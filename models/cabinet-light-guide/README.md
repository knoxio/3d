# Cabinet light guide

Channel that holds a 2 mm LED strip under a cabinet panel, just behind the
front edge, and hides it behind a fascia. Two runs: one under the cabinet top,
one under the wood mid shelf. Each lights its half of the cabinet, passing
through the glass shelf below it.

## Pieces

| File | Qty per run | Size |
| --- | --- | --- |
| `light_guide-guide.3mf` | 2 | 193.3 × 20 × 15 (includes the 8 mm tongue) |
| `light_guide-guide-end.3mf` | 1 | 185.3 × 20 × 15 |

Three pieces butt to 556 mm inside a 560 mm opening. Two runs: 4 × `guide`,
2 × `guide-end`.

## Parameters

| Variable | Default | Meaning |
| --- | --- | --- |
| `inner_w` | 560 | clear width between the side panels |
| `side_clear` | 2 | gap at each end of a run |
| `pieces` | 3 | pieces per run |
| `depth` | 20 | front to back |
| `plate_t` | 2.4 | plate that takes the tape |
| `fascia_t` / `drop` | 3 / 15 | fascia thickness and how far it hangs down |
| `seat_front` / `seat_z` | 8 / 6 | where the strip seat starts, and its depth below the panel |
| `seat_tilt` | 11.3 | seat angle, aiming the strip down and back |
| `strip_w` / `strip_clear` | 2 / 0.6 | strip width and channel clearance |
| `rib` | [1, 1] | retaining rib width and height |
| `tongue_*`, `tongue_fit` | 8 / 1.2 / 0.2 | splice tongue and its clearance |

## Hiding the strip

The strip sits 11 mm behind the fascia and 5 mm below the panel; the fascia
hangs 15 mm. A viewer has to be about 1 m below the guide for every 1 m they
stand back before the strip comes into view, so standing or seated it stays
hidden. Light leaves downward and toward the back of the cabinet; rays steeper
than ~43° also pass under the fascia to light the front of the shelf.

## Print

- P1S, PLA, 0.2 mm layers, 3 walls, 15 % infill, **no supports**.
- Orientation is baked in: the flat tape face is on the bed.
- ~22 cm³ per piece, so roughly 30 g each.

## Fitting

- 3M VHB (12 mm) along the flat top face. Clean the panel first.
- Set the fascia front face flush with the panel's front edge, or 1–2 mm
  behind it. Check the top hinge arm clears the fascia when the door shuts.
- The strip's lead runs along the open channel behind the fascia to the right
  end, then out to the side panel.

## Assumptions

- 560 mm is the clear inside width; both runs are the same width.
- Strip is 2 mm wide, ≤ 1 mm thick, self-adhesive, emitting from its face.
- Front edges are flush (no face frame lip below the panel).

## Status

draft — not yet printed.
