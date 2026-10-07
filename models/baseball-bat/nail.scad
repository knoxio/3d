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

// parts: nail test

part = "nail"; // [nail, test]

/* [The shell, measured off the mesh] */
hex_flats = 8.47;       // mm, across the flats
shell_wall = 2.54;      // mm

/* [Fit] */
fit = 0.25;             // mm off the flats; the test print settles this
grip = 0;               // mm the lip stands proud, each side: 0 is a press fit
plug_bore = 5.4;        // mm, hollow so the lip's legs can give
slots = 4;              // they start at the bore, not the axis
slot_w = 1.1;           // mm
lead_in = 0.7;          // mm of 45 deg chamfer at the entering end
behind = 1.0;           // mm the plug reaches past the inner surface

/* [Nail] */
head_d = 12;            // mm at its widest
spike_d = 7;            // mm where it leaves the head
spike_len = 32;         // mm clear of the shell
tip_d = 1.4;            // mm: blunt enough to print, and to carry about

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

module nail(fit = fit, grip = grip, spike = spike_len, label = "", slots = slots) {
    plug_d = hex_flats - fit;
    head_h = (head_d - plug_d) / 2;         // 45 deg
    difference() {
        union() {
            translate([0, 0, -plug_len])
                cylinder(d1 = plug_d - 2 * lead_in, d2 = plug_d, h = lead_in);
            translate([0, 0, -plug_len]) cylinder(d = plug_d, h = plug_len);
            if (grip > 0) translate([0, 0, -plug_len])
                cylinder(d1 = plug_d - 2 * lead_in, d2 = plug_d + 2 * grip, h = lead_in + grip);
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

module test() {
    for (i = [0 : len(test_fits) - 1])
        translate([i * test_pitch, 0, plug_len])
            nail(fit = test_fits[i], grip = 0, spike = test_spike, label = str(i + 1));
    for (i = [0 : len(test_grips) - 1])
        translate([(len(test_fits) + i) * test_pitch, 0, plug_len])
            nail(fit = test_grips[i], grip = 0.45, spike = test_spike, slots = test_slots[i]);
}

echo(str("ladder: plug Ø", hex_flats - test_fits[len(test_fits) - 1], " to Ø",
         hex_flats - test_fits[0], " into a Ø", hex_flats, " hex; 7 and 8 have a lip"));

if (part == "test") test();
else nail();
