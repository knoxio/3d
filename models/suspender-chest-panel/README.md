# Suspender chest panel

A 200 × 80 mm black PLA chest panel with bowed top and bottom edges and raised white stag, foliage, and border, worn behind suspenders.

## Parameters

| Variable | Default | Meaning |
| --- | --- | --- |
| `panel_width` | 200 mm | Complete printed width, including the ends behind the suspenders |
| `panel_height` | 80 mm | Complete printed height |
| `base_thickness` | 1.2 mm | Thin solid black backing for gentle flex |
| `edge_round_radius` | 0.5 mm | Roundover along the upper 3D edge of the black base |
| `bottom_chamfer` | 0.2 mm | 45-degree lower edge bevel for support-free printing |
| `edge_round_segments` | 10 | Quarter-circle roundover resolution |
| `edge_skin` | 0.001 mm | Loft cross-section thickness |
| `relief_height` | 0.6 mm | White detailing above the backing |
| `corner_radius` | 3 mm | Rounded panel corners |
| `top_curve_rise` | 12 mm | Top edge rises at the centre relative to the ends |
| `bottom_curve_drop` | 14 mm | Bottom edge drops at the centre relative to the ends |
| `curve_segments` | 100 | Even number of segments per curved edge |
| `border_inset` | 5 mm | Border distance from the panel edge |
| `border_width` | 1.2 mm | White border line width |
| `artwork_width` | 166 mm | Width of the drawing canvas after scaling |
| `artwork_height` | 62 mm | Height of the drawing canvas after scaling |
| `art_canvas_width` / `art_canvas_height` | 200 / 80 mm | Artwork coordinate system in `_ornament.scad` |
| `part` | `assembled` | `base`, `detailing`, or `assembled` |

The curved outline follows the shallow arched top and bowed bottom of the [Vintage Brown suspender chest bridge](https://lederhosens.com/products/vintage-brown-premium-lederhosen-suspenders-aosus-24). It remains 200 × 80 mm overall, with narrower ends hidden behind the suspenders. The white border follows the same curves. The black base has a 0.5 mm radius along its upper 3D perimeter and a 0.2 mm, 45-degree lower chamfer; its underside stays flat on the bed. This rounds the thickness edge without changing the top-view outline.

The original vector artwork is `_ornament.scad`, drawn from the supplied photo as a stylised stag and foliage rather than an exact tracing. Smooth Bezier curves, rounded antlers, a recessed eye, and outlined leaves use explicit geometric unions so overlapping strokes cannot cancel each other out.

## Print

Bambu P1S, **0.2 mm nozzle**, black and white PLA through AMS. Use 0.1 mm layers, 3 walls, and 100% infill. Print flat back down; no supports, raft, or brim required. Total thickness is 1.2 mm in plain areas and 1.8 mm under the relief. That is 12 black layers plus 6 relief layers. PLA permits gentle bending across this broad thin panel; it is not intended to fold or repeatedly crease. Print flexibility has not been tested.

Build with `mise run build suspender-chest-panel`.

Open **`chest_panel-project.3mf`** in Bambu Studio as a project. It contains one assembled object with black backing on filament 1 and white relief on filament 2, preserving the white part's Z=1.2 mm placement. The project sets the P1S 0.2 mm nozzle and 0.1 mm layers; match its black and white filament entries to the physical AMS slots before printing.

The project generator uses `_project_settings.json`, a factory settings template from Bambu Studio 02.08.02.61, plus the two current mesh exports. It builds without requiring Bambu Studio or personal printer configuration.

The separate `chest_panel-base.3mf` and `chest_panel-detailing.3mf` files remain available for other slicers. Import both as a single multipart object without dropping the detailing onto the plate. `chest_panel-assembled.3mf` is a connected inspection mesh with face colours; the project uses actual filament assignments instead.

Leave attachment areas solid. Place the panel behind the actual suspenders, mark the fastener locations, then drill holes matched to the chosen thumbtack pins. No pin diameter or hole spacing has been guessed. Keep drilled holes clear of the outer edges and decorative border.

Preview: `chest_panel-assembled.png`; front view can be generated with:

```sh
openscad --hardwarnings --backend manifold -o out/suspender-chest-panel/chest_panel-front.png --render --camera=0,0,0,0,0,0,250 --projection=o --imgsize=1600,800 --colorscheme=Tomorrow models/suspender-chest-panel/chest_panel.scad
```

Validation: `python3 models/suspender-chest-panel/_test_chest_panel.py`, `python3 models/suspender-chest-panel/_test_project.py`, `python3 tools/_test_build.py`, and `mise run check`. Bambu Studio 02.08.02.61 command-line slicing was verified using only the embedded settings: 18 layers, both filaments, and a tool change to white. The validation slice estimated about 23.3 g including purge material; print time depends on the active material and speed settings.

## Assumptions

The owner specified 200 × 80 mm, placement behind the suspenders, AMS printing, a 0.2 mm nozzle, and drilling after fitting. Base thickness, relief height, edge curvature, rounded corners, decorative border, and artwork proportions are design choices. The panel is initially flat; any curvature comes from gentle flex when worn. The suspenders may obscure the border at the ends.

## Status

draft — previews, geometry tests, project tests, and native Bambu slicing checked; physical print and flex not yet verified.
