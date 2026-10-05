// Wrist-worn controller enclosure, built around an existing perfboard build.
//
// Origin (0,0,0) is the corner of the green perfboard at the elbow end, front
// edge, at the board's TOP face. X runs toward the hand, Y across the arm
// (front edge to back edge), Z up. Every measured value below is in that
// frame, so numbers here can be compared directly against calipers on the
// bench.

// parts: base lid-elbow lid-hand

part = "assembly"; // [assembly, base, lid-elbow, lid-hand]

/* [Boards] */
green = [70, 30, 1.5];      // perfboard, X by Y by thickness
black = [18.5, 25.6];       // KY-040 board, butted against the green one
black_gap = 0.5;            // measured 88.7-89 assembled against 88.5 butted
green_hole_d = 2.5;
green_hole_inset = 2.45;    // centres, from both edges
black_hole_d = 3.5;
black_hole_x = 85.75;       // centres, in the shared frame
black_hole_y = [6.95, 23.05];

/* [Stack heights, from the board's top face] */
wire_space = 5.5;           // under the board, for the loom (dressed flat)
button_base = 6;            // board to the underside of the button body
button_h = 6;               // button body height
screen_rise = 8;            // board to the underside of the screen module
screen_pcb_t = 1.2;
screen_glass_t = 1.8;
screen_slack = 1.0;         // the screen measured ~1 mm proud of the buttons
usb_rise = 4;               // board to the underside of the USB-C shell
usb_h = 3.2;

/* [Buttons] */
button_d = 6;
button_hole_d = 7.5;        // clearance absorbs the +-0.7 the gaps disagree by
button_x = 60.5;
button_y = [8.4, 16.2, 24.0];

/* [Knob] */
shaft = [78.2, 13.2];       // measured four ways, closing within 0.35 mm
bush_d = 6.85;
knob_d = 14.5;
knob_clear = 2.5;           // total, around the knob
knob_bottom = 11;           // board to the underside of the knob
knob_top = 17;              // board to the top of the knob

/* [Screen, mounted to the elbow lid] */
screen_pcb = [35.5, 33.5];
screen_at = [0.1, 3.5];     // PCB corner in the shared frame (rough)
screen_hole_d = 3.5;
screen_hole_inset = [1.3, 2.55];   // from the PCB edges, x then y
glass = [34.5, 18.6];
glass_inset = [0.5, 8.3];   // glass corner from the PCB corner
glass_lip = 3.8;            // unlit strip along the glass's front edge
window_margin = 0.8;        // window cut back from the lit area

/* [Case] */
clear_elbow = 5;            // board edge to the inner wall
clear_front = 2.6;
clear_back = 6.5;           // covers the screen's 7 mm overhang
clear_hand = 3.5;
wall = 2;
floor_t = 2;
lid_t = 2;
ceiling_slack = 1.5;        // above the screen, the tallest thing inside
flange_w = 8;               // the cap's landing on the base's rim
hand_top = 8.5;             // board to the lid over buttons and knob: they stand proud
corner_r = 4;
forearm_r = 40;             // underside curve; measure and correct
seam_x = 46;                // lid split, clear of screen and buttons

/* [Fixings] */
insert_d = 3.2;             // M2 heat-set insert pilot
insert_depth = 4;
screw_d = 2.2;
screw_head_d = 4;
boss_d = 6;
// The screen hangs with its glass against the roof, so its pads are only as
// deep as the glass is thick: too shallow for an insert, so M2 self-tappers.
screen_screw_d = 1.7;
screen_screw_depth = 3;

/* [Openings] */
usb_opening = [13, 6.5];    // generous: the socket's Y position is unmeasured
usb_y = 15;
wire_exit_d = 6;
wire_exit = [2, 15];
strap_w = 24;               // velcro band width
strap_gap = 3.5;            // slot height: band thickness plus slack
strap_lug_len = 52;         // along the arm
strap_lug_h = 13;           // down the flank, so the band hides the case's height
strap_bar = 3.0;            // the bar the band pulls against
strap_slot_len = 34;        // the opening itself

$fa = 2;
$fs = 0.4;

inner = [
    [-clear_elbow, -clear_front],
    [green[0] + black[0] + black_gap + clear_hand, green[1] + clear_back],
];
outer = [
    [inner[0][0] - wall, inner[0][1] - wall],
    [inner[1][0] + wall, inner[1][1] + wall],
];
// Two ceilings: the screen sets the tall half, the hand half only has to clear
// the encoder body — buttons and knob stand proud through their openings.
top_screen = screen_rise + screen_pcb_t + screen_glass_t + screen_slack + ceiling_slack;
top_hand = hand_top;
inner_top = top_screen;
floor_z = -(wire_space + green[2]);           // inner floor, below the board
size_xy = [outer[1][0] - outer[0][0], outer[1][1] - outer[0][1]];

echo(str("case ", size_xy[0], " x ", size_xy[1],
         " x ", top_screen - floor_z + floor_t + lid_t, " mm at the screen, ",
         top_hand - floor_z + floor_t + lid_t, " mm at the knob"));

module rounded_block(lo, hi, z0, z1, r) {
    hull() for (x = [lo[0] + r, hi[0] - r], y = [lo[1] + r, hi[1] - r])
        translate([x, y, z0]) cylinder(r = r, h = z1 - z0);
}

module forearm_cut() {
    // the underside curls around the arm; the cylinder runs along X
    translate([0, (outer[0][1] + outer[1][1]) / 2, floor_z - floor_t - forearm_r + 2])
        rotate([0, 90, 0])
            cylinder(r = forearm_r, h = size_xy[0] + 40, center = true);
}

module stepped(lo, hi, z0, tall_z, low_z, r, split) {
    // tall over the screen, low over the knob, with a 45 degree face between
    // them so the cap prints without support and shrugs off a knock
    intersection() {
        rounded_block(lo, hi, z0, tall_z, r);
        union() {
            translate([lo[0] - 1, lo[1] - 1, z0])
                cube([split - lo[0] + 1, hi[1] - lo[1] + 2, tall_z - z0]);
            translate([lo[0] - 1, lo[1] - 1, z0])
                cube([hi[0] - lo[0] + 2, hi[1] - lo[1] + 2, low_z - z0]);
            translate([split, lo[1] - 1, low_z])
                rotate([-90, 0, 0])
                    linear_extrude(hi[1] - lo[1] + 2)
                        polygon([[0, 0], [0, tall_z - low_z], [-(tall_z - low_z), tall_z - low_z]]);
        }
    }
}

// The base is one height all round; the extra height the screen needs belongs
// to its lid, which is a raised cap rather than a flat plate. The outer
// envelope is shared, so the cap and the base agree on the seam.
module shell() {
    difference() {
        stepped(outer[0], outer[1], floor_z - floor_t,
                top_screen + lid_t, top_hand + lid_t, corner_r, seam_x);
        forearm_cut();
    }
}

module base_shell() {
    difference() {
        rounded_block(outer[0], outer[1], floor_z - floor_t, top_hand, corner_r);
        forearm_cut();
    }
}

module cavity() {
    rounded_block(inner[0], inner[1], floor_z, top_screen + lid_t + 1,
                  max(corner_r - wall, 1));
}

module boss(x, y, h) {
    translate([x, y, floor_z]) difference() {
        cylinder(d = boss_d, h = h);
        translate([0, 0, h - insert_depth]) cylinder(d = insert_d, h = insert_depth + 1);
    }
}

module board_bosses() {
    for (x = [green_hole_inset, green[0] - green_hole_inset],
         y = [green_hole_inset, green[1] - green_hole_inset])
        boss(x, y, wire_space);
    for (y = black_hole_y) boss(black_hole_x, y, wire_space);
}

module lid_posts(x0, x1, top) {
    for (x = [x0 + boss_d / 2 + 1, x1 - boss_d / 2 - 1],
         y = [inner[0][1] + boss_d / 2, inner[1][1] - boss_d / 2])
        boss(x, y, top - floor_z);
}

module strap_lugs() {
    // The band crosses the arm, so it threads through the long sides. Each lug
    // is a tall plate held off the flank by a post at either end: the band
    // passes up the gap behind it, open top and bottom, and covers the case's
    // height on the way. A tab on the end of the case could not do that — the
    // band would run along the arm instead of around it.
    mid_x = (outer[0][0] + outer[1][0]) / 2;
    top_z = top_hand + lid_t;   // the low half sets it, so the lug clears both lids
    z_hi = top_z - 1.5;
    z_lo = z_hi - strap_lug_h;
    bar_r = strap_bar / 2;
    post = 4.5;
    for (side = [0, 1]) {
        y = side ? outer[1][1] : outer[0][1];
        dir = side ? 1 : -1;
        translate([mid_x, y, 0]) {
            hull() for (x = [-1, 1] * (strap_slot_len / 2 - bar_r),
                        z = [z_lo + bar_r, z_hi - bar_r])
                translate([x, dir * (strap_gap + bar_r), z])
                    sphere(r = bar_r);
            for (x = [-1, 1] * (strap_slot_len / 2 + post / 2 - 1))
                hull() for (z = [z_lo + bar_r, z_hi - bar_r])
                    translate([x, dir * (strap_gap + strap_bar) / 2, z])
                        rotate([90, 0, 0])
                            cylinder(d = post, h = strap_gap + strap_bar + 2, center = true);
        }
    }
}

module openings() {
    translate([outer[0][0] - 1, usb_y, usb_rise + usb_h / 2])
        rotate([0, 90, 0])
            hull() for (dy = [-1, 1] * (usb_opening[0] / 2 - usb_opening[1] / 2))
                translate([0, dy, 0]) cylinder(d = usb_opening[1], h = wall + 2);
    translate([wire_exit[0], wire_exit[1], floor_z - floor_t - 1])
        cylinder(d = wire_exit_d, h = floor_t + 2);
}

module base() {
    difference() {
        union() {
            difference() {
                base_shell();
                cavity();
            }
            board_bosses();
            lid_posts(inner[0][0], seam_x, top_hand);
            lid_posts(seam_x, inner[1][0], top_hand);
            strap_lugs();
        }
        openings();
    }
}

module lid(x0, x1, top) {
    difference() {
        intersection() {
            shell();
            translate([x0, outer[0][1] - 1, top])
                cube([x1 - x0, size_xy[1] + 2, lid_t]);
        }
        for (x = [x0 + boss_d / 2 + 1, x1 - boss_d / 2 - 1],
             y = [inner[0][1] + boss_d / 2, inner[1][1] - boss_d / 2])
            if (x > x0 && x < x1) translate([x, y, top - 1]) {
                cylinder(d = screw_d, h = lid_t + 2);
                translate([0, 0, lid_t + 1 - 1.2]) cylinder(d = screw_head_d, h = 1.4);
            }
    }
}

module lid_hand() {
    difference() {
        lid(seam_x, outer[1][0] + 1, top_hand);
        for (y = button_y)
            translate([button_x, y, top_hand - 1]) cylinder(d = button_hole_d, h = lid_t + 2);
        translate([shaft[0], shaft[1], top_hand - 1])
            cylinder(d = knob_d + knob_clear, h = lid_t + 2);
    }
}

module lid_elbow() {
    // A raised cap: a flange that lands on the base's rim, walls and a roof
    // over the screen, and the screen hung from that roof on its own holes.
    // The screen sits lower than the flange, so the flange is cut away over
    // it. The hand end of the roof ramps down to the flange, which both
    // closes the cap and keeps the slope printable.
    lit = [glass[0] - 2 * 2.55, glass[1] - glass_lip];
    lit_at = [screen_at[0] + glass_inset[0] + 2.55,
              screen_at[1] + glass_inset[1] + glass_lip];
    difference() {
        union() {
            difference() {
                intersection() {
                    shell();
                    translate([outer[0][0] - 1, outer[0][1] - 1, top_hand])
                        cube([seam_x - outer[0][0] + 1, size_xy[1] + 2,
                              top_screen + lid_t - top_hand]);
                }
                rounded_block(inner[0], inner[1], top_hand + lid_t,
                              top_screen, max(corner_r - wall, 1));
            }
            for (x = [screen_at[0] + screen_hole_inset[0],
                      screen_at[0] + screen_pcb[0] - screen_hole_inset[0]],
                 y = [screen_at[1] + screen_hole_inset[1],
                      screen_at[1] + screen_pcb[1] - screen_hole_inset[1]])
                translate([x, y, top_screen - screen_glass_t])
                    cylinder(d = boss_d, h = screen_glass_t);
        }
        // the flange is a frame, not a plate: the ESP and the MPU stand up
        // into this level, and the screen pokes right through it
        rounded_block([inner[0][0] + flange_w, inner[0][1] + flange_w],
                      [seam_x - (top_screen - top_hand) - 2, inner[1][1] - flange_w],
                      top_hand - 1, top_hand + lid_t + 1, corner_r);
        translate([screen_at[0] - 1, screen_at[1] - 1, top_hand - 1])
            cube([screen_pcb[0] + 2, screen_pcb[1] + 2, lid_t + 2]);
        translate([lit_at[0] + window_margin, lit_at[1] + window_margin, top_screen - 1])
            cube([lit[0] - 2 * window_margin, lit[1] - 2 * window_margin, lid_t + 2]);
        for (x = [screen_at[0] + screen_hole_inset[0],
                  screen_at[0] + screen_pcb[0] - screen_hole_inset[0]],
             y = [screen_at[1] + screen_hole_inset[1],
                  screen_at[1] + screen_pcb[1] - screen_hole_inset[1]])
            translate([x, y, top_screen - screen_glass_t - 1])
                cylinder(d = screen_screw_d, h = screen_screw_depth + 1);
        for (x = [inner[0][0] + boss_d / 2 + 1, seam_x - boss_d / 2 - 1],
             y = [inner[0][1] + boss_d / 2, inner[1][1] - boss_d / 2])
            translate([x, y, top_hand - 1]) {
                cylinder(d = screw_d, h = lid_t + 2);
                translate([0, 0, lid_t + 1 - 1.2]) cylinder(d = screw_head_d, h = 1.4);
            }
    }
}

module assembly() {
    color("DimGray") base();
    color("SlateGray") lid_elbow();
    color("LightSlateGray") lid_hand();
    color("DarkGreen", 0.5) translate([0, 0, -green[2]]) cube([green[0], green[1], green[2]]);
    color("Black", 0.5) translate([green[0] + black_gap, (green[1] - black[1]) / 2, -green[2]])
        cube([black[0], black[1], green[2]]);
}

if (part == "assembly") assembly();
else if (part == "base") base();
else if (part == "lid-elbow") lid_elbow();
else if (part == "lid-hand") lid_hand();
