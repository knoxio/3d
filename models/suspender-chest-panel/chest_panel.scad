// parts: base detailing assembled
include <_ornament.scad>
part = "assembled";

panel_width = 200; // mm
panel_height = 80; // mm
base_thickness = 1.2; // mm
edge_round_radius = 0.5; // mm, upper perimeter roundover
bottom_chamfer = 0.2; // mm, 45-degree print-safe lower edge
edge_round_segments = 10; // segments in the quarter-circle profile
edge_skin = 0.001; // mm, loft cross-section thickness
relief_height = 0.6; // mm
corner_radius = 3; // mm
top_curve_rise = 12; // mm, centre above ends
bottom_curve_drop = 14; // mm, centre below ends
curve_segments = 100; // number of segments per curved edge, even
border_inset = 5; // mm
border_width = 1.2; // mm
artwork_width = 166; // mm
artwork_height = 62; // mm
$fa = 1;
$fs = 0.4;

assert(panel_width > 2 * (border_inset + border_width + corner_radius));
assert(panel_height > 2 * (border_inset + border_width + corner_radius));
assert(top_curve_rise >= 0 && bottom_curve_drop >= 0);
assert(top_curve_rise + bottom_curve_drop < panel_height - 2 * (border_inset + border_width + corner_radius));
assert(curve_segments >= 4 && curve_segments % 2 == 0);
assert(base_thickness >= 1.2);
assert(edge_round_radius > 0 && bottom_chamfer > 0);
assert(edge_round_radius + bottom_chamfer < base_thickness);
assert(edge_round_segments >= 4);
assert(edge_skin > 0 && edge_skin < bottom_chamfer);
assert(edge_round_radius < border_inset);
assert(relief_height >= 0.6);
assert(artwork_width <= panel_width - 2 * (border_inset + border_width));
assert(artwork_height <= panel_height - 2 * (border_inset + border_width));
assert(part == "base" || part == "detailing" || part == "assembled");

/** Bowed chest bridge footprint with rounded ends and a fixed overall envelope. */
module outline() {
    inner_half_width = panel_width / 2 - corner_radius;
    inner_half_height = panel_height / 2 - corner_radius;
    offset(r = corner_radius)
        polygon(concat(
            [for (i = [0:curve_segments])
                let(u = 2 * i / curve_segments - 1)
                [u * inner_half_width, inner_half_height - top_curve_rise * u * u]],
            [for (i = [curve_segments:-1:0])
                let(u = 2 * i / curve_segments - 1)
                [u * inner_half_width, -inner_half_height + bottom_curve_drop * u * u]]
        ));
}

module _edge_section(z, inset) {
    translate([0, 0, min(z, base_thickness - edge_skin)])
        linear_extrude(height = edge_skin)
            offset(delta = -inset) outline();
}

/** Thin backing with a rounded top rim, 45-degree lower chamfer, and flat bed face. */
module base() {
    hull() {
        _edge_section(0, bottom_chamfer);
        _edge_section(bottom_chamfer, 0);
    }
    translate([0, 0, bottom_chamfer])
        linear_extrude(height = base_thickness - edge_round_radius - bottom_chamfer)
            outline();
    for (i = [0:edge_round_segments-1]) {
        angle_a = 90 * i / edge_round_segments;
        angle_b = 90 * (i+1) / edge_round_segments;
        hull() {
            _edge_section(base_thickness - edge_round_radius + edge_round_radius * sin(angle_a),
                          edge_round_radius * (1-cos(angle_a)));
            _edge_section(base_thickness - edge_round_radius + edge_round_radius * sin(angle_b),
                          edge_round_radius * (1-cos(angle_b)));
        }
    }
}

/** Relief positioned on the backing; retain its Z offset when importing as an AMS part. */
module detailing() {
    translate([0, 0, base_thickness])
        linear_extrude(height = relief_height)
            union() {
                difference() {
                    offset(delta = -border_inset) outline();
                    offset(delta = -border_inset - border_width) outline();
                }
                scale([artwork_width / art_canvas_width,
                       artwork_height / art_canvas_height])
                    ornament();
            }
}

if (part == "base") base();
if (part == "detailing") detailing();
if (part == "assembled") {
    color("black") base();
    color("white") detailing();
}
