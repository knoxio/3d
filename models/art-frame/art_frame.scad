// Segmented LED frame for a 1100 x 600 relief tile artwork (200 mm tile grid).
//
// Frame coordinates: the art occupies [0, art_w] x [0, art_h] on the wall,
// z points away from the wall. Each side is built in a local frame:
//   X = along the side, Y = inset from the outer edge (0 outside, face_w
//   inside), Z = off the wall.
//
// Joints are dovetails that slide in from the art side (+Y). The socket is
// open only on the inner face below the tile height, so it is hidden behind
// the tiles; front, outside and back show a plain seam.

// parts: corner-bl corner-br corner-tl corner-tr straight-tt straight-st fit-test-0.05 fit-test-0.10

part = "assembly"; // [assembly, corner-bl, corner-br, corner-tl, corner-tr, straight-tt, straight-st, fit-test-0.05, fit-test-0.10]

/* [Art] */
art_w = 1100;          // mm
art_h = 600;           // mm
art_depth = 15;        // mm, tile height off the wall
art_gap = 1.5;         // mm, gap between tiles and frame inner face

/* [Profile] */
face_w = 40;           // mm, frame width seen from the front
depth = 35;            // mm, frame height off the wall
bevel = 4;             // mm, 45 degree bevel on both front edges

/* [LED slot] */
led_z = 23;            // mm, LED centre off the wall (8 above the tiles)
slot_h = 5;            // mm, slot height at the back wall
slot_d = 8;            // mm, slot depth into the frame
slot_tilt = 10;        // deg, slot floor/ceiling slope down toward the art
slot_corner_r = 5;     // mm, strip bend radius at the corners

/* [Segmentation] */
seam_x = [100, 300, 500, 700, 900]; // mm, art coords, on tile seams
seam_y = [200, 400];                // mm, art coords, on tile seams

/* [Dovetail] */
tail_len = 10;         // mm, protrusion past the seam
tail_root = [3, 12];   // mm, Z span at the seam
tail_tip = [1.5, 13.5];// mm, Z span at the tip
tail_skin = 4;         // mm, outer skin left in front of the tail (Y)
fit = 0.10;            // mm, clearance per flank (0.15 tested: slightly loose)
seat_fit = 0.2;        // mm, extra clearance at the tip and seat

/* [Cable] */
cable_x = 1000;        // mm, art x where the cable channel crosses the bottom
cable_w = 6;           // mm
cable_d = 5;           // mm, groove depth into the back face
lead_hole = [4, 34];   // mm, [width in Y, Y start] of the hole from slot to groove

$fa = 2;
$fs = 0.4;

ox = -art_gap - face_w;                 // outer edge in art coords
outer_w = art_w + 2 * (art_gap + face_w);
outer_h = art_h + 2 * (art_gap + face_w);
leg_l = seam_x[0] - ox;                 // bottom-left / top-left horizontal leg
leg_r = art_w - seam_x[len(seam_x) - 1] - ox;
leg_b = seam_y[0] - ox;
leg_t = art_h - seam_y[len(seam_y) - 1] - ox;
straight_len = seam_x[1] - seam_x[0];
assert(
    [for (i = [1 : len(seam_x) - 1]) seam_x[i] - seam_x[i - 1]] == [for (i = [1 : len(seam_x) - 1]) straight_len]
        && seam_y[1] - seam_y[0] == straight_len,
    "all straight pieces must share one length"
);

slot_drop = slot_d * tan(slot_tilt);
slot_back = face_w - slot_d;

function profile() = [
    [0, 0],
    [face_w, 0],
    [face_w, led_z - slot_h / 2 - slot_drop],
    [slot_back, led_z - slot_h / 2],
    [slot_back, led_z + slot_h / 2],
    [face_w, led_z + slot_h / 2 - slot_drop],
    [face_w, depth - bevel],
    [face_w - bevel, depth],
    [bevel, depth],
    [0, depth - bevel],
];

module bar(x0, x1) {
    translate([x0, 0, 0]) rotate([90, 0, 90])
        linear_extrude(x1 - x0) polygon(profile());
}

// Tail pointing +X from a seam at X = 0. With `c` > 0 it becomes the socket
// cutter: flanks grow by c, the seat and tip by seat_fit, and it opens past
// the seam and the inner face.
module tail(c = 0) {
    s = c > 0 ? seat_fit : 0;
    y_end = face_w + (c > 0 ? 1 : 0);
    module slice(x, y0, zs)
        translate([x, y0, zs[0] - c]) cube([0.01, y_end - y0, zs[1] - zs[0] + 2 * c]);
    hull() {
        slice(0, tail_skin - s, tail_root);
        slice(tail_len + s, tail_skin + tail_len - s, tail_tip);
    }
    if (c > 0) hull() {
        slice(-1, tail_skin - s, tail_root);
        slice(0, tail_skin - s, tail_root);
    }
}

module socket(c = fit) { tail(c); }

module straight(left, right) {
    difference() {
        union() {
            bar(0, straight_len);
            if (left == "tail") mirror([1, 0, 0]) tail();
            if (right == "tail") translate([straight_len, 0, 0]) tail();
        }
        if (left == "socket") socket();
        if (right == "socket") translate([straight_len, 0, 0]) mirror([1, 0, 0]) socket();
    }
}

module cable_cut(at) {
    translate([at - cable_w / 2, -1, -1]) cube([cable_w, face_w + 2, cable_d + 1]);
    translate([at - cable_w / 2, lead_hole[1], cable_d - 0.5])
        cube([cable_w, lead_hole[0], led_z - cable_d]);
}

// One leg along +X from the outer corner, mitred on Y <= X, socket at the far end.
module leg(len, cable_at) {
    difference() {
        intersection() {
            bar(0, len);
            linear_extrude(depth + 1) polygon([[0, 0], [len + 1, 0], [len + 1, len + 1]]);
        }
        translate([len, 0, 0]) mirror([1, 0, 0]) socket();
        if (!is_undef(cable_at)) cable_cut(cable_at);
    }
}

module slot_fillet() {
    z0 = led_z - slot_h / 2 - slot_drop - 1;
    translate([0, 0, z0]) linear_extrude(slot_h + 2 + slot_drop)
        difference() {
            translate([slot_back - 0.01, slot_back - 0.01]) square(slot_corner_r + 0.01);
            translate([slot_back + slot_corner_r, slot_back + slot_corner_r]) circle(slot_corner_r);
        }
}

// X leg length a, Y leg length b; cable channel optional on the Y leg.
module corner(a, b, cable_on_b) {
    union() {
        leg(a);
        mirror([1, -1, 0]) leg(b, cable_on_b);
        slot_fillet();
    }
}

corners = [
    // name,        world origin,             rot, X leg, Y leg, cable on Y leg
    ["corner-bl", [ox, ox],                    0,  leg_l, leg_b, undef],
    ["corner-br", [ox + outer_w, ox],          90, leg_b, leg_r, ox + outer_w - cable_x],
    ["corner-tr", [ox + outer_w, ox + outer_h], 180, leg_r, leg_t, undef],
    ["corner-tl", [ox, ox + outer_h],          270, leg_t, leg_l, undef],
];

function corner_def(name) = [for (c = corners) if (c[0] == name) c][0];

module corner_named(name) {
    c = corner_def(name);
    corner(c[3], c[4], c[5]);
}

// Print orientation: one leg lying on its outer face, the other standing up.
// The longer leg lies down; on a tie, the leg with the cable channel does, so
// the groove prints as a vertical slot.
module print_corner(name) {
    c = corner_def(name);
    x_leg_down = c[3] > c[4] || (c[3] == c[4] && is_undef(c[5]));
    if (x_leg_down) rotate([90, 0, 0]) corner_named(name);
    else rotate([0, -90, 0]) corner_named(name);
}

module print_straight(left, right) {
    rotate([90, 0, 0]) straight(left, right);
}

module side_straights(count, start) {
    for (i = [0 : count - 1])
        translate([start + i * straight_len, 0, 0])
            if (i == 0) straight("tail", "tail");
            else straight("socket", "tail");
}

module assembly() {
    for (c = corners)
        translate(c[1]) rotate(c[2]) color("SteelBlue") corner(c[3], c[4], c[5]);
    color("LightSteelBlue") {
        translate([ox, ox]) side_straights(len(seam_x) - 1, leg_l);
        translate([ox + outer_w, ox]) rotate(90) side_straights(len(seam_y) - 1, leg_b);
        translate([ox + outer_w, ox + outer_h]) rotate(180) side_straights(len(seam_x) - 1, leg_r);
        translate([ox, ox + outer_h]) rotate(270) side_straights(len(seam_y) - 1, leg_t);
    }
    color("Wheat", 0.6) cube([art_w, art_h, art_depth]);
}

// Short socket-only coupon to test a clearance against an existing tail.
// The clearance is debossed on the back.
coupon_len = 30;
module fit_coupon(c) {
    difference() {
        bar(0, coupon_len);
        socket(c);
        translate([(tail_len + coupon_len) / 2 + 1, face_w / 2, -0.01])
            linear_extrude(0.6) mirror([1, 0, 0])
                text(str(c), size = 5, halign = "center", valign = "center");
    }
}

if (part == "assembly") assembly();
else if (part == "fit-test-0.05") rotate([90, 0, 0]) fit_coupon(0.05);
else if (part == "fit-test-0.10") rotate([90, 0, 0]) fit_coupon(0.10);
else if (part == "straight-tt") print_straight("tail", "tail");
else if (part == "straight-st") print_straight("socket", "tail");
else print_corner(part);
