// Battery door for the bat's knob: a new knob end with a twist-lock socket,
// and the cap that closes it.
//
// The original knob is a hollow cone behind a Ø26.4 hole, with nothing square
// to latch on, so its bottom 25 mm is replaced rather than cut into. The
// outside keeps the original silhouette; the cap forms the lower chamfer.
//
// Z is the bat's own axis, 0 at its very bottom. The socket and the cap meet
// on the plane z = chamfer.

// parts: socket-test cap

part = "assembly"; // [assembly, socket-test, cap, clash]

/* [The knob, as the original mesh has it] */
knob_r = 25;            // mm, widest radius
neck_r = 20;            // mm, outside of the handle
bore_r = 17.5;          // mm, inside of the handle
chamfer = 5;            // mm, both 45 deg chamfers between neck_r and knob_r
knob_h = 25;            // mm, bottom of the bat to where the knob is handle again

/* [Twist lock: a three-start, part-turn thread] */
lugs = 3;
lug_arc = 40;           // deg
notch_arc = 46;         // deg, the gap each lug enters through
lug_out = 3.0;          // mm the lugs stand out from the plug
lip_t = 4.5;            // mm, lip thickness at the bore where the cap seats
seat_angle = 55;        // deg of turn at which the cap pulls up tight
lead = 12.6;            // mm of travel per full turn
lug_top = 8.8;          // mm, top of the lugs above the mating face
radial_fit = 0.2;       // mm per side, plug in bore
lug_fit = 0.3;          // mm, lug tips to the cavity wall

/* [Cap] */
plug_wall = 3.3;        // mm
bay_floor = 3.5;        // mm of cap left under the hollow for the connector
coin_slot = [24, 3, 1.5];   // mm, length, width, depth

/* [Checks] */
test_h = 25;            // mm of knob end in the test piece
turn = 55;              // deg, cap position in the assembly and clash views
gap = 0;                // mm the cap is pulled back out, same views

$fa = 2;
$fs = 0.4;

mate = chamfer;                         // z of the mating plane
rise = lead / 360;                      // mm per degree
plug_r = bore_r - radial_fit;
lug_r = plug_r + lug_out;
cavity_r = lug_r + lug_fit;
cavity_top = mate + lug_top + 2.4;      // lugs clear this even with the cap hard in
segment = [notch_arc / 2, 360 / lugs - notch_arc / 2];   // deg, each lip segment
slice = 2;                              // deg, facet of the helical faces

// Both faces of the lock are 45 deg cones on the same helix, so they bear
// over their whole area and centre the cap as it tightens.
function seat_z(a) = mate + lip_t + rise * (a - seat_angle);

assert(seat_z(segment[0]) - mate >= 3, "the lip is too thin where a lug enters");
assert(seat_z(segment[1]) + cavity_r - bore_r < cavity_top - 1, "the lip runs into the cavity roof");
assert(mate + lug_top - (seat_z(seat_angle + lug_arc / 2) + lug_r - bore_r) >= 0.6,
       "the lugs come to a feather edge");
assert(seat_angle - lug_arc / 2 >= segment[0] && seat_angle + lug_arc / 2 <= segment[1],
       "a seated lug is not wholly under the lip");

module helix(a0, a1) {
    n = ceil((a1 - a0) / slice);
    da = (a1 - a0) / n;
    for (i = [0 : n - 1])
        rotate([0, 0, a0 + i * da])
            rotate_extrude(angle = da + 0.02)
                children($a = a0 + (i + 0.5) * da);
}

module socket(top) {
    roof_z = cavity_top + cavity_r - bore_r;
    rotate_extrude()
        polygon([[cavity_r, mate], [knob_r, mate], [knob_r, knob_h - chamfer],
                 [neck_r, knob_h], [neck_r, top], [bore_r, top],
                 [bore_r, roof_z], [cavity_r, cavity_top]]);
    for (k = [0 : lugs - 1]) rotate([0, 0, k * 360 / lugs])
        helix(segment[0], segment[1])
            polygon([[bore_r, mate], [cavity_r + 0.01, mate],
                     [cavity_r + 0.01, seat_z($a) + cavity_r - bore_r],
                     [bore_r, seat_z($a)]]);
}

module cap() {
    top = mate + lug_top;
    difference() {
        union() {
            rotate_extrude()
                polygon([[0, 0], [neck_r, 0], [knob_r, mate], [0, mate]]);
            cylinder(r = plug_r, h = top);
        }
        translate([0, 0, bay_floor]) cylinder(r = plug_r - plug_wall, h = top);
        translate([0, 0, coin_slot[2] / 2 - 0.01])
            cube([coin_slot[0], coin_slot[1], coin_slot[2]], center = true);
    }
    for (k = [0 : lugs - 1]) rotate([0, 0, k * 360 / lugs])
        helix(-lug_arc / 2, lug_arc / 2)
            polygon([[plug_r - 0.01, seat_z(seat_angle + $a) + plug_r - bore_r],
                     [lug_r, seat_z(seat_angle + $a) + lug_r - bore_r],
                     [lug_r, top], [plug_r - 0.01, top]]);
}

module placed_cap() {
    translate([0, 0, -gap]) rotate([0, 0, turn]) cap();
}

if (part == "socket-test") translate([0, 0, -mate]) socket(mate + test_h);
else if (part == "cap") cap();
else if (part == "clash") intersection() { socket(mate + test_h); placed_cap(); }
else {
    color("SaddleBrown") difference() {
        socket(mate + test_h);
        translate([0, -60, -1]) cube([60, 60, 80]);
    }
    color("Goldenrod") placed_cap();
}
