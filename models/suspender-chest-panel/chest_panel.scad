// parts: base detailing assembled
part = "assembled";

panel_width = 200; // mm
panel_height = 80; // mm
base_thickness = 1.2; // mm
relief_height = 0.6; // mm
corner_radius = 3; // mm
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
assert(base_thickness >= 1.2);
assert(relief_height >= 0.6);
assert(artwork_width <= panel_width - 2 * (border_inset + border_width));
assert(artwork_height <= panel_height - 2 * (border_inset + border_width));
assert(part == "base" || part == "detailing" || part == "assembled");

/** Rounded panel footprint, centred on the origin. */
module outline() {
    offset(r = corner_radius)
        square([panel_width - 2 * corner_radius,
                panel_height - 2 * corner_radius], center = true);
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
