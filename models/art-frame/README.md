# Art frame

Segmented LED frame around a 1100 × 600 mm relief tile artwork (200 mm tile
grid, one half-width column). The tiles are stuck to the wall; the frame sits
flat on the wall around them with a 1.5 mm gap and never overlaps a tile, so
tiles lift straight off. A 2 mm LED strip in a hidden slot rakes light across
the relief.

## Pieces (14)

| File | Qty | Size (print orientation) |
| --- | --- | --- |
| `art_frame-corner-bl.3mf` | 1 | 35 × 241.5 × 141.5 |
| `art_frame-corner-tl.3mf` | 1 | 241.5 × 35 × 141.5 |
| `art_frame-corner-br.3mf` | 1 | 35 × 241.5 × 241.5 — has the cable channel |
| `art_frame-corner-tr.3mf` | 1 | 241.5 × 35 × 241.5 |
| `art_frame-straight-tt.3mf` | 4 | 220 × 35 × 40 — tails on both ends |
| `art_frame-straight-st.3mf` | 6 | 210 × 35 × 40 — socket one end, tail the other |

Seams fall on tile seams: x = 100, 300, 500, 700, 900 and y = 200, 400 (art
coordinates, origin bottom-left of the art, half column on the left).

Placement, going along each side from its corner: the first straight is a
`tt`, the rest are `st` with the socket towards the `tt`. Short sides have
one `tt` each.

## Profile

40 wide × 35 deep. Flat back and outside, flat 32 mm front face with 4 mm 45°
bevels on both front edges. LED slot on the inner face: 5 mm tall, 8 mm deep,
floor and ceiling sloped 10° down toward the art, strip centre 23 mm off the
wall (8 mm above the tiles). The slot top edge is level with the strip, so the
LED is not visible from the front.

## Joints

Dovetail tail 10 mm long, flaring 9 → 12 mm, 1.5–13.5 mm off the wall, on a
45° seat. It slides in from the art side, so the socket opens only on the
inner face below tile height — hidden behind the tiles. Front, outside and
back show a plain seam. Clearance 0.10 mm per flank, 0.2 mm at the seat
(0.15 printed slightly loose).

Assembly: lay everything face-down on the floor, glue each joint and slide
the tail in from the art side. Finish with a middle straight of any side.

## Cable

`corner-br`: 6 × 5 mm groove across the back at x = 1000 (the bottom-right
tile), plus a 6 × 4 mm hole from the groove up into the LED slot. The lead
drops from the slot into the groove; the groove runs to the tile on one side
and down the wall on the other.

## Parameters

All in `art_frame.scad`, top of file: art size and gap, `face_w`, `depth`,
`bevel`, LED slot (`led_z`, `slot_h`, `slot_d`, `slot_tilt`,
`slot_corner_r`), seams (`seam_x`, `seam_y` — all straights must share one
length), dovetail (`tail_*`, `fit`, `seat_fit`), cable (`cable_x`, `cable_w`,
`cable_d`, `lead_hole`).

## Print

- P1S, PLA, 0.2 mm layers, 3 walls, 15 % infill (gyroid), no supports.
- Orientation is baked into the files: every piece lies on its **outer**
  face. Corners have the other leg standing up (141.5 or 241.5 mm tall) — use
  a brim and consider slowing outer walls for the tall ones.
- `art_frame-fit-test-0.05` / `-0.10`: 30 mm socket-only coupons, clearance
  debossed on the back. Try them against any printed tail; set `fit` to the
  one that slides in snug, rebuild, then print the rest. Only sockets depend
  on `fit`, so already-printed tails stay compatible.
- Solid model volume is ~4.8 L; at the settings above expect roughly
  1.5–2 kg of filament in total.

## Assumptions

- Tile grid half column is on the **left** (from the photo). If it moves to
  the right, change `seam_x` to `[200, 400, 600, 800, 1000]` and `cable_x`.
- Strip is ≤ 2 mm wide, ≤ 1 mm thick, emits from its face.

## Status

test print: one `tt` + one `st` at `fit` 0.15 — joint works, slightly loose.
Fit lowered to 0.10; coupons added to confirm before the full run.
