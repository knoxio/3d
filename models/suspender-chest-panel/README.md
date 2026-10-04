# Suspender chest panel

A 200 × 80 mm black PLA chest panel with bowed top and bottom edges and raised white stag, foliage, and border, worn behind suspenders.

## Parameters

| Variable | Default | Meaning |
| --- | --- | --- |
| `panel_width` | 200 mm | Complete printed width, including the ends behind the suspenders |
| `panel_height` | 80 mm | Complete printed height |
| `base_thickness` | 1.2 mm | Thin solid black backing for gentle flex |
| `relief_height` | 0.6 mm | White detailing above the backing |
| `corner_radius` | 3 mm | Rounded panel corners |
| `top_curve_rise` | 12 mm | Top edge rises at the centre relative to the ends |
| `bottom_curve_drop` | 14 mm | Bottom edge drops at the centre relative to the ends |
| `curve_segments` | 100 | Even number of segments per curved edge |
| `border_inset` | 5 mm | Border distance from the panel edge |
| `border_width` | 1.2 mm | White border line width |
| `artwork_width` | 166 mm | Width of the SVG drawing canvas after scaling |
| `artwork_height` | 62 mm | Height of the SVG drawing canvas after scaling |
| `reference_width` / `reference_height` | 200 / 80 mm | SVG source canvas; retain these unless editing the SVG canvas |
| `part` | `assembled` | `base`, `detailing`, or `assembled` |

The curved outline follows the shallow arched top and bowed bottom of the [Vintage Brown suspender chest bridge](https://lederhosens.com/products/vintage-brown-premium-lederhosen-suspenders-aosus-24). It remains 200 × 80 mm overall, with narrower ends hidden behind the suspenders. The white border follows the same curves.

The original vector artwork is `_ornament.svg`, drawn from the supplied photo as a stylised stag and foliage rather than an exact tracing.

## Print

Bambu P1S, **0.2 mm nozzle**, black and white PLA through AMS. Use 0.1 mm layers, 3 walls, and 100% infill. Print flat back down; no supports, raft, or brim required. Total thickness is 1.2 mm in plain areas and 1.8 mm under the relief. That is 12 black layers plus 6 relief layers. PLA permits gentle bending across this broad thin panel; it is not intended to fold or repeatedly crease. Print flexibility has not been tested.

Build with `mise run build suspender-chest-panel`.

For reliable AMS part assignment, select **both** `chest_panel-base.3mf` and `chest_panel-detailing.3mf` together in Bambu Studio and import them as a **single object with multiple parts**. Preserve their relative positions: white detailing starts at Z=1.2 mm and sits on the black base. Assign black to the base and white to the detailing. Do not arrange or drop the detailing onto the plate independently.

`chest_panel-assembled.3mf` is a single connected mesh with black/white face colours; use it for inspection or if the slicer preserves its colour assignments. The separate-part import avoids relying on that behaviour.

Leave attachment areas solid. Place the panel behind the actual suspenders, mark the fastener locations, then drill holes matched to the chosen thumbtack pins. No pin diameter or hole spacing has been guessed. Keep drilled holes clear of the outer edges and decorative border.

Preview: `chest_panel-assembled.png`; front view can be generated with:

```sh
openscad --hardwarnings --backend manifold -o out/suspender-chest-panel/chest_panel-front.png --render --camera=0,0,0,0,0,0,250 --projection=o --imgsize=1600,800 --colorscheme=Tomorrow models/suspender-chest-panel/chest_panel.scad
```

Validation: `python3 models/suspender-chest-panel/_test_chest_panel.py` and `mise run check`. Time and filament estimates depend on the slicer settings and have not been measured.

## Assumptions

The owner specified 200 × 80 mm, placement behind the suspenders, AMS printing, a 0.2 mm nozzle, and drilling after fitting. Base thickness, relief height, edge curvature, rounded corners, decorative border, and artwork proportions are design choices. The panel is initially flat; any curvature comes from gentle flex when worn. The suspenders may obscure the border at the ends.

## Status

draft — rendered and geometry checked; not test printed or worn.
