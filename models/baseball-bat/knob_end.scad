// Battery door for the bat's knob: a new knob end with a twist-lock socket,
// the cap that closes it, and the sleeve that guides the pack up the handle.
//
// The original knob is a hollow cone behind a Ø26.4 hole, with nothing square
// to latch on, so its bottom 25 mm is replaced rather than cut into. The
// outside keeps the original silhouette; the cap forms the lower chamfer.
//
// Z is the bat's own axis, 0 at its very bottom. The socket and the cap meet
// on the plane z = chamfer.

// parts: socket-test cap sleeve plate

part = "assembly"; // [assembly, socket-test, cap, sleeve, plate, clash, sleeve-clash]

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

/* [Pack: 2 x 18650 inline, shrink-wrapped, both leads out of one end] */
pack_d = 20.5;          // mm, at its thickest
pack_len = 131.4;       // mm, without the leads
pack_fit = 0.4;         // mm per side in the sleeve
pack_play = 1.0;        // mm of end float

/* [Sleeve] */
sleeve_wall = 1.6;      // mm
sleeve_fit = 0.3;       // mm per side in the handle bore
bay_len = 45;           // mm of open bay under the pack, for leads and connectors
shoulder_z = 160.3;     // mm, where the bore starts closing at 45 deg to the first joint
spigot_bore_r = 15.32;  // mm, the bore through that joint
stop_land = 1.2;        // mm, width of the face that lands on the shoulder
ring_h = 5;             // mm, guide ring under that face
end_play = 0.5;         // mm the sleeve floats between the cap and the shoulder
fins = 3;
fin_t = 2;              // mm
channel_w = 6;          // mm, slot for the bat's own lead to reach the bay
top_stop_r = 7;         // mm, opening left at the top of the sleeve
post_d = 9;             // mm, the cap's post that holds the pack up off its leads
post_gap = 1.0;         // mm between the post and the pack

/* [Checks] */
test_h = 25;            // mm of knob end in the test piece
turn = 55;              // deg, cap position in the assembly and clash views
gap = 0;                // mm the cap is pulled back out, same views
plate_gap = 14;         // mm between pieces on the bed
lift = 0;               // mm the sleeve is raised, sleeve-clash view

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

// The sleeve stands on the cap's plug and slides in the handle bore. Swung, the
// pack is thrown toward the tip, so the sleeve's top takes that load and passes
// it to the shoulder inside the first joint; the cap only holds things up.
sleeve_r = bore_r - sleeve_fit;
tube_ri = pack_d / 2 + pack_fit;
tube_ro = tube_ri + sleeve_wall;
sleeve_z0 = mate + lug_top;
funnel_h = sleeve_r - sleeve_wall - tube_ri;        // 45 deg, bay down to the tube
pack_z0 = sleeve_z0 + bay_len + funnel_h;
pack_z1 = pack_z0 + pack_len + pack_play;
sleeve_top = pack_z1 + tube_ri - top_stop_r + 1;
stop_z = shoulder_z + stop_land + sleeve_fit - end_play;   // top of the landing face
ring_z = stop_z - stop_land - ring_h;                      // foot of the guide ring
shed = 0.8;             // mm the outer cones sit above the inner, to keep the wall

assert(tube_ro + 1 < spigot_bore_r, "the sleeve's nose does not pass the first joint");
assert(ring_z - (sleeve_r - tube_ro) > sleeve_z0 + bay_len + shed + funnel_h,
       "the guide ring runs into the bay");
assert(pack_z1 > stop_z, "the pack ends below the shoulder: shorten the bay");
assert(sleeve_top - sleeve_z0 <= 245, "the sleeve is taller than the P1S prints");
assert(post_d / 2 + 2 < tube_ri - 4, "the post reaches the edge of the pack, where its leads are");

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
    // The pack's leads leave the edge of its end, so a post up the middle can
    // carry the pack without touching them, at any angle the cap stops at.
    post_tip = pack_z0 - post_gap;
    difference() {
        union() {
            translate([0, 0, bay_floor - 0.01]) cylinder(r1 = post_d, r2 = post_d / 2, h = post_d / 2);
            translate([0, 0, bay_floor]) cylinder(d = post_d, h = post_tip - bay_floor - 1);
            translate([0, 0, post_tip - 1]) cylinder(d1 = post_d, d2 = post_d - 2, h = 1);
        }
        translate([0, 0, bay_floor + 2]) cylinder(d = post_d - 2 * sleeve_wall, h = post_tip);
    }
    for (k = [0 : lugs - 1]) rotate([0, 0, k * 360 / lugs])
        helix(-lug_arc / 2, lug_arc / 2)
            polygon([[plug_r - 0.01, seat_z(seat_angle + $a) + plug_r - bore_r],
                     [lug_r, seat_z(seat_angle + $a) + lug_r - bore_r],
                     [lug_r, top], [plug_r - 0.01, top]]);
}

module sleeve() {
    bay_top = sleeve_z0 + bay_len;
    difference() {
        union() {
            rotate_extrude()
                polygon([[sleeve_r - sleeve_wall, sleeve_z0], [sleeve_r, sleeve_z0],
                         [sleeve_r, bay_top + shed],
                         [tube_ro, bay_top + shed + sleeve_r - tube_ro],
                         [tube_ro, ring_z - (sleeve_r - tube_ro)],
                         [sleeve_r, ring_z], [sleeve_r, stop_z - stop_land],
                         [sleeve_r - stop_land, stop_z], [tube_ro, stop_z],
                         [tube_ro, sleeve_top], [top_stop_r, sleeve_top],
                         [top_stop_r, sleeve_top - 1], [tube_ri, pack_z1],
                         [tube_ri, pack_z0], [sleeve_r - sleeve_wall, bay_top]]);
            for (k = [0 : fins - 1]) rotate([90, 0, (k + 0.5) * 360 / fins])
                linear_extrude(fin_t, center = true)
                    polygon([[tube_ro - 0.1, bay_top + shed + sleeve_r - tube_ro],
                             [sleeve_r, bay_top + shed], [sleeve_r, ring_z + 0.1],
                             [tube_ro - 0.1, ring_z - (sleeve_r - tube_ro)]]);
        }
        translate([tube_ro + 0.01, -channel_w / 2, sleeve_z0 - 1])
            cube([sleeve_r, channel_w, sleeve_top]);
    }
}

// Not printed: the pack, and the handle with its first joint, for the preview.
module pack_ghost() {
    color("RoyalBlue") translate([0, 0, pack_z0 + pack_play / 2]) cylinder(d = pack_d - 1, h = pack_len);
}

module handle_ghost(top) {
    color("Peru", 0.35) rotate_extrude()
        polygon([[bore_r, mate + test_h], [neck_r, mate + test_h], [neck_r, top], [bore_r, top],
                 [bore_r, 180], [spigot_bore_r, 180],
                 [spigot_bore_r, shoulder_z + bore_r - spigot_bore_r], [bore_r, shoulder_z]]);
}

module placed_cap() {
    translate([0, 0, -gap]) rotate([0, 0, turn]) cap();
}

module socket_test() {
    translate([0, 0, -mate]) socket(mate + test_h);
}

if (part == "socket-test") socket_test();
else if (part == "cap") cap();
else if (part == "plate") {
    translate([knob_r, knob_r, 0]) socket_test();
    translate([3 * knob_r + plate_gap, knob_r, 0]) cap();
    translate([4 * knob_r + 2 * plate_gap + sleeve_r, knob_r, -sleeve_z0]) sleeve();
}
else if (part == "sleeve") translate([0, 0, -sleeve_z0]) sleeve();
else if (part == "clash") intersection() { socket(mate + test_h); placed_cap(); }
else if (part == "sleeve-clash") intersection() {
    translate([0, 0, lift]) sleeve();
    union() { socket(mate + test_h); placed_cap(); }
}
else difference() {
    union() {
        color("SaddleBrown") socket(mate + test_h);
        handle_ghost(sleeve_top + 12);
        color("Goldenrod") placed_cap();
        color("Gainsboro") sleeve();
        pack_ghost();
    }
    translate([0, -60, -1]) cube([60, 60, sleeve_top + 40]);
}
