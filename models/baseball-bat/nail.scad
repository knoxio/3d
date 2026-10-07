// Nails for the bat's honeycomb: a spike on a flared head, plugged into a hexagon.
//
// The hexagons are a straight prism through the shell — 8.47 across the flats,
// 9.40 across the corners, unchanged from bore to outside, in a 2.54 wall.
//
// The plug is round rather than hexagonal, sized to the flats, so it bears on
// all six and goes in at any rotation: with twenty of these to push home, not
// having to clock each one is worth more than the corner contact.
//
// The head is a 45 degree cone rather than a disc. A disc would have to be
// dished to sit on a Ø78.6 shell, and printed plug-down its rim would be a
// 2.4 mm overhang on the very face that has to seat. A cone seats on its inner
// edge whatever the curvature, prints without support, and looks like a stud.
//
// Z is the nail's axis, 0 at the shell's outer surface, pointing outward. It
// prints as modelled: plug on the bed, spike up.

// parts: nail test fit nails

part = "nail"; // [nail, test, fit, nails]

/* [The shell, measured off the mesh] */
hex_flats = 8.47;       // mm, across the flats
shell_wall = 2.54;      // mm

/* [Fit] */
// Ladder one put Ø8.50 tight and Ø8.30 snug; ladder two put Ø8.40 in without
// strain and Ø8.45 not at all. So the hole prints close to its drawn 8.47, and
// a plug that goes everywhere is Ø8.35 — the barb, not the fit, does the
// holding, which also covers the printed hexagons being slightly squashed.
fit = 0.12;             // mm off the flats
hex_plug = false;       // bears on the whole flat, but has to be clocked, and
                        // cannot give where a hexagon came out squashed
grip = 0.4;             // mm the lip stands proud, each side: 0 is a press fit
plug_bore = 5.0;        // mm, hollow so the lip's legs can give
slots = 4;              // they start at the bore, not the axis
slot_w = 1.1;           // mm
lead_in = 0.7;          // mm of chamfer at the entering end
lip_h = 1.4;            // mm from the plug's end to the lip's catch face
behind = 1.0;           // mm the catch sits past the inner surface

/* [Nail] */
head_d = 12;            // mm at its widest
spike_d = 7;            // mm where it leaves the head
spike_len = 32;         // mm clear of the shell
tip_d = 1.4;            // mm: blunt enough to print, and to carry about

/* [A batch of nails] */
count = 24;
plate_pitch = 18;       // mm, clear of the Ø12 heads
per_row = 8;

/* [Test ladder] */
test_spike = 12;        // mm, a stub: this is about the fit, not the look
test_fits = [-0.03, 0.17, 0.37, 0.57, 0.77, 0.97];
// a hollow, slotted plug has no middle to number, so these two are told apart
// by their slots: two on the first, four on the second
test_grips = [0.37, 0.57];
test_slots = [2, 4];
test_pitch = 16;        // mm between pieces

$fa = 2;
$fs = 0.3;

plug_len = shell_wall + behind;

// The plug reaches past the wall far enough to put the lip's CATCH outside it,
// not the lip's tip. Getting that wrong buries the barb in the hole, where it
// grips by friction when it grips at all.
function plug_depth(grip) = shell_wall + behind + (grip > 0 ? lip_h : 0.6);

// hex is passed in, not read from the global: a module does not see its
// caller's locals, so reading it here silently printed every plug round
module prism(d, h, taper = 0, hex = hex_plug) {
    if (hex) rotate([0, 0, 90])
        cylinder(r1 = (d - 2 * taper) / sqrt(3), r2 = d / sqrt(3), h = h, $fn = 6);
    else cylinder(d1 = d - 2 * taper, d2 = d, h = h);
}

module nail(fit = fit, grip = grip, spike = spike_len, label = "", slots = slots,
            hex_plug = hex_plug) {
    plug_d = hex_flats - fit;
    plug_len = plug_depth(grip);
    head_h = (head_d - plug_d) / 2;         // 45 deg
    difference() {
        union() {
            translate([0, 0, -plug_len]) prism(plug_d, plug_len, hex = hex_plug);
            if (grip > 0) translate([0, 0, -plug_len]) {
                prism(plug_d + 2 * grip, lip_h, taper = lead_in + grip, hex = hex_plug);
                translate([0, 0, lip_h - 0.01]) prism(plug_d, 0.02, hex = hex_plug);
            } else translate([0, 0, -plug_len])
                prism(plug_d, lead_in, taper = lead_in, hex = hex_plug);
            cylinder(d1 = plug_d, d2 = head_d, h = head_h);
            translate([0, 0, head_h]) cylinder(d1 = spike_d, d2 = tip_d, h = spike);
        }
        if (grip > 0) {
            translate([0, 0, -plug_len - 0.01]) cylinder(d = plug_bore, h = plug_len + 0.5);
            for (k = [0 : slots - 1]) rotate([0, 0, k * 360 / slots])
                translate([-slot_w / 2, plug_bore / 2 - 0.3, -plug_len - 0.01])
                    cube([slot_w, plug_d, plug_len + 0.4]);
        }
        // the number goes on the end you are looking at as you push it in,
        // and on the bed, so it comes out crisp
        if (label != "")
            translate([0, 0, -plug_len - 0.01])
                linear_extrude(0.45)
                    text(label, size = 3.4, halign = "center", valign = "center",
                         font = "Liberation Sans:style=Bold");
    }
}

// Second ladder: the plug sizes the first one pointed at, now with the barb's
// catch where it belongs, and the same two sizes as hexagons for comparison.
// 1-3 and 5 are numbered; 4 and 6 are the slotted ones, round and hex.
fit_round = [0.02, 0.07, 0.12];
fit_snap = 0.12;
fit_hexes = [0.07, 0.12];

module fit() {
    for (i = [0 : 2]) translate([i * test_pitch, 0, plug_depth(0)])
        nail(fit = fit_round[i], spike = test_spike, label = str(i + 1));
    translate([3 * test_pitch, 0, plug_depth(0.4)])
        nail(fit = fit_snap, grip = 0.4, spike = test_spike);
    translate([4 * test_pitch, 0, plug_depth(0)])
        nail(fit = fit_hexes[0], spike = test_spike, label = "5", hex_plug = true);
    translate([5 * test_pitch, 0, plug_depth(0.4)])
        nail(fit = fit_hexes[1], grip = 0.4, spike = test_spike, hex_plug = true);
}

module nails() {
    for (i = [0 : count - 1])
        translate([(i % per_row) * plate_pitch, floor(i / per_row) * plate_pitch,
                   plug_depth(grip)])
            nail();
}

module test() {
    for (i = [0 : len(test_fits) - 1])
        translate([i * test_pitch, 0, plug_len])
            nail(fit = test_fits[i], grip = 0, spike = test_spike, label = str(i + 1));
    for (i = [0 : len(test_grips) - 1])
        translate([(len(test_fits) + i) * test_pitch, 0, plug_len])
            nail(fit = test_grips[i], grip = 0.45, spike = test_spike, slots = test_slots[i]);
}

echo(str("nail: plug Ø", hex_flats - fit, ", ", plug_depth(grip), " deep, catch ",
         behind, " past a ", shell_wall, " wall; ", spike_len + (head_d - (hex_flats - fit)) / 2,
         " mm proud of the bat"));

if (part == "nails") nails();
else if (part == "fit") fit();
else if (part == "test") test();
else nail();
