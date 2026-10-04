// parts: base detailing assembled
part = "assembled";

panel_width = 200; // mm
panel_height = 80; // mm
base_thickness = 1.2; // mm
relief_height = 0.6; // mm
corner_radius = 3; // mm
top_curve_rise = 12; // mm, centre above ends
bottom_curve_drop = 14; // mm, centre below ends
curve_segments = 100; // number of segments per curved edge, even
border_inset = 5; // mm
border_width = 1.2; // mm
artwork_width = 166; // mm
artwork_height = 62; // mm
reference_width = 200; // mm, SVG drawing canvas
reference_height = 80; // mm, SVG drawing canvas
$fa = 1;
$fs = 0.4;

assert(panel_width > 2 * (border_inset + border_width + corner_radius));
assert(panel_height > 2 * (border_inset + border_width + corner_radius));
assert(top_curve_rise >= 0 && bottom_curve_drop >= 0);
assert(top_curve_rise + bottom_curve_drop < panel_height - 2 * (border_inset + border_width + corner_radius));
assert(curve_segments >= 4 && curve_segments % 2 == 0);
assert(base_thickness >= 1.2);
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

/** Solid backing resting on Z=0. */
module base() {
    linear_extrude(height = base_thickness) outline();
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
                scale([artwork_width / reference_width,
                       artwork_height / reference_height])
                    import("_ornament.svg", center = true);
            }
}

if (part == "base") base();
if (part == "detailing") detailing();
if (part == "assembled") {
    color("black") base();
    color("white") detailing();
}
