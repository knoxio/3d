// parts: base detailing assembled
include <_ornament.scad>
part = "assembled";

strap_outer_width = 240; // mm, outside edge to outside edge of both suspenders
strap_width = 30; // mm, each suspender
tab_diameter = 28; // mm
body_width = strap_outer_width - 2 * strap_width; // mm, visible middle between straps
panel_width = body_width + tab_diameter; // mm, semicircular tabs project half a diameter each
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

assert(body_width == strap_outer_width - 2 * strap_width);
assert(panel_width == body_width + tab_diameter);
assert(panel_width <= 245 && panel_height <= 245);
assert(strap_width > 0 && tab_diameter / 2 <= strap_width);
assert(tab_diameter > 2 * edge_round_radius && tab_diameter < panel_height);
assert(body_width > 2 * (border_inset + border_width + corner_radius));
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
assert(artwork_width <= body_width - 2 * (border_inset + border_width));
assert(artwork_height <= panel_height - 2 * (border_inset + border_width));
assert(part == "base" || part == "detailing" || part == "assembled");

/** Bowed chest bridge footprint with rounded ends and a fixed overall envelope. */
module body_outline() {
    inner_half_width = body_width / 2 - corner_radius;
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

module _edge_section(z, inset, side) {
    translate([0, 0, min(z, base_thickness - edge_skin)])
        linear_extrude(height = edge_skin)
            offset(delta = -inset)
                if (side == 0) body_outline();
                else translate([side * body_width / 2, 0]) circle(d = tab_diameter);
}

module _rounded_solid(side) {
    hull() {
        _edge_section(0, bottom_chamfer, side);
        _edge_section(bottom_chamfer, 0, side);
    }
    hull() {
        _edge_section(bottom_chamfer, 0, side);
        _edge_section(base_thickness - edge_round_radius, 0, side);
    }
    for (i = [0:edge_round_segments-1]) {
        angle_a = 90 * i / edge_round_segments;
        angle_b = 90 * (i+1) / edge_round_segments;
        hull() {
            _edge_section(base_thickness - edge_round_radius + edge_round_radius * sin(angle_a),
                          edge_round_radius * (1-cos(angle_a)), side);
            _edge_section(base_thickness - edge_round_radius + edge_round_radius * sin(angle_b),
                          edge_round_radius * (1-cos(angle_b)), side);
        }
    }
}

/** Thin rounded backing with integral semicircular strap tabs and a flat bed face. */
module base() {
    _rounded_solid(0);
    for (side = [-1,1]) _rounded_solid(side);
}

/** Relief positioned on the backing; retain its Z offset when importing as an AMS part. */
module detailing() {
    translate([0, 0, base_thickness])
        linear_extrude(height = relief_height)
            union() {
                difference() {
                    offset(delta = -border_inset) body_outline();
                    offset(delta = -border_inset - border_width) body_outline();
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
