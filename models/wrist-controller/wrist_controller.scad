// Wrist-worn controller enclosure, built around an existing perfboard build.
//
// Origin (0,0,0) is the corner of the green perfboard at the elbow end, front
// edge, at the board's TOP face. X runs toward the hand, Y across the arm
// (front edge to back edge), Z up. Every measured value below is in that
// frame, so numbers here can be compared directly against calipers on the
// bench.

// parts: base lid-elbow lid-hand plate

part = "assembly"; // [assembly, base, lid-elbow, lid-hand, plate]

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
button_hole_d = 7.0;        // clearance absorbs the +-0.7 the gaps disagree by
button_x = 60.5;
button_y = [8.4, 16.2, 24.0];

/* [Knob] */
shaft = [78.2, 13.2];       // measured four ways, closing within 0.35 mm
bush_d = 6.85;              // the threaded bush: what the lid has to clear
knob_clear = 1.15;          // total, around the bush
knob_d = 14.5;              // the knob's skirt, which hides the hole
knob_bottom = 11;           // board to the underside of the knob

/* [Screen, mounted to the elbow lid] */
screen_pcb = [35.5, 33.5];
screen_at = [0.1, 3.5];     // PCB corner in the shared frame (rough)
screen_hole_d = 3.5;
screen_hole_inset = [1.3, 2.55];   // from the PCB edges, x then y
glass = [34.5, 18.6];
glass_inset = [0.5, 8.3];   // glass corner from the PCB corner
glass_lip = 3.8;            // unlit strip along the glass's front edge
glass_bezel = 1.8;          // unlit border along the long edges
window_margin = 0.4;        // how far the window opens past the lit area
glass_seat = 0.4;           // roof left over the glass's edge, to hold it
window_bevel = 1.2;         // 45 deg flare on the outside, for the viewing angle
label = "PURGE";
label_size = 6;             // mm, cap height
label_depth = 0.4;          // two layers at 0.2, for a filament swap
label_font = "Liberation Sans:style=Bold";

/* [Case] */
clear_elbow = 5;            // board edge to the inner wall
clear_front = 2.6;
clear_back = 7.5;           // the screen overhangs the board's back edge by 7
clear_hand = 3.5;
wall = 2;
floor_t = 2;
lid_t = 2;
ceiling_slack = 1.5;        // above the screen, the tallest thing inside
tab_d = 7.5;                // the cap's screw tabs, its only landing on the rim
hand_top = 8.5;             // board to the lid over buttons and knob: they stand proud
corner_r = 4;
seam_x = 46;                // lid split, clear of screen and buttons

/* [Fixings] */
insert_d = 3.2;             // M2 heat-set insert pilot
insert_depth = 4;
screw_d = 2.2;
screw_head_d = 4;
boss_d = 6;
// Where the boards leave no room for an insert's boss, the screw taps its own
// thread in a slimmer one.
tap_boss_d = 4;
tap_pilot_d = 1.7;
tap_depth = 6;
// The screen's glass sits straight against the roof; these pins pass through
// its own Ø3.5 holes and are flattened with a hot iron to hold it there.
screen_pin_d = 3.2;
screen_stake = 1.5;         // how far a pin stands proud of the PCB

/* [Openings] */
usb_opening = [13, 6.5];    // generous: the socket's width is assumed, not measured
usb_socket_w = 9;           // assumed; the measured gap is to its back edge
usb_y = green[1] - 7.5 - usb_socket_w / 2;
wire_exit_d = 3;            // two wires out to the battery
wire_exit = [8, -0.6];      // centre: the front elbow corner, clear of the post
strap_gap = 3.5;            // slot height: band thickness plus slack
strap_lug_drop = 1.5;       // how far below the lid the lug's top sits
strap_bar = 4.0;            // the bar the band pulls against
strap_slot_len = 52;        // the opening: far wider than the 24 mm band, so
                            // the pull is spread along the flank

bed = [256, 256];           // P1S build plate
plate_gap = 6;              // between pieces on the bed

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

// The window shows the lit area, opened a little past it and then held back
// from the glass's own edge so the roof still has something to seat the glass
// against. Both the window and the staking pins come off the same four
// mounting holes, so neither depends on where the screen floats above the
// board.
glass_at = [screen_at[0] + glass_inset[0], screen_at[1] + glass_inset[1]];
lit_at = [glass_at[0] + glass_bezel, glass_at[1] + glass_lip];
lit = [glass[0] - 2 * glass_bezel, glass[1] - glass_lip];
win_lo = [for (i = [0, 1]) max(lit_at[i] - window_margin, glass_at[i] + glass_seat)];
win_hi = [for (i = [0, 1]) min(lit_at[i] + lit[i] + window_margin,
                               glass_at[i] + glass[i] - glass_seat)];
size_xy = [outer[1][0] - outer[0][0], outer[1][1] - outer[0][1]];

// What the boards occupy, as [x0, y0, x1, y1] — the one thing a lid post may
// not stand in, at any height, because the boards go in from above.
board_rects = [[0, 0, green[0], green[1]],
               [green[0] + black_gap, (green[1] - black[1]) / 2,
                green[0] + black_gap + black[0], (green[1] + black[1]) / 2]];

function fouled_by(f) =
    let (r = (f[2] ? tap_boss_d : boss_d) / 2)
    [for (b = board_rects)
        if (min(f[0] + r, b[2]) > max(f[0] - r, b[0]) &&
            min(f[1] + r, b[3]) > max(f[1] - r, b[1])) b];

assert(len([for (l = ["elbow", "hand"], f = fixings(l))
            if (len(fouled_by(f)) > 0) f]) == 0,
       "a lid post stands in a board's footprint");

assert([for (f = fixings("elbow"), h = screen_holes())
            if (norm([f[0] - h[0], f[1] - h[1]]) < (tab_d + screen_pin_d) / 2 + 0.3) f] == [],
       "a screw tab runs into a screen pin");

// A tab's top face and the screen PCB's underside are both at top_hand + lid_t,
// so a tab reaching under the PCB would press on whatever is on its back.
assert([for (f = fixings("elbow"))
            if (min(f[0] + tab_d / 2, screen_at[0] + screen_pcb[0]) > max(f[0] - tab_d / 2, screen_at[0]) &&
                min(f[1] + tab_d / 2, screen_at[1] + screen_pcb[1]) > max(f[1] - tab_d / 2, screen_at[1])) f] == [],
       "a screw tab reaches under the screen");

assert(knob_bottom >= top_hand + lid_t, "the knob fouls the hand lid");
assert(knob_d > bush_d + knob_clear + 2, "the knob no longer hides its hole");

echo(str("window ", win_hi[0] - win_lo[0], " x ", win_hi[1] - win_lo[1],
         " mm over a lit area of ", lit[0], " x ", lit[1],
         ", flaring to ", win_hi[0] - win_lo[0] + 2 * window_bevel, " x ",
         win_hi[1] - win_lo[1] + 2 * window_bevel, " outside"));
echo(str("case ", size_xy[0], " x ", size_xy[1],
         " x ", top_screen - floor_z + floor_t + lid_t, " mm at the screen, ",
         top_hand - floor_z + floor_t + lid_t, " mm at the knob"));

module rounded_block(lo, hi, z0, z1, r) {
    hull() for (x = [lo[0] + r, hi[0] - r], y = [lo[1] + r, hi[1] - r])
        translate([x, y, z0]) cylinder(r = r, h = z1 - z0);
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
    stepped(outer[0], outer[1], floor_z - floor_t,
            top_screen + lid_t, top_hand + lid_t, corner_r, seam_x);
}

module base_shell() {
    rounded_block(outer[0], outer[1], floor_z - floor_t, top_hand, corner_r);
}

module cavity() {
    rounded_block(inner[0], inner[1], floor_z, top_screen + lid_t + 1,
                  max(corner_r - wall, 1));
}

module boss(x, y, h, tapped = false) {
    translate([x, y, floor_z]) difference() {
        cylinder(d = tapped ? tap_boss_d : boss_d, h = h);
        translate([0, 0, h - (tapped ? tap_depth : insert_depth)])
            cylinder(d = tapped ? tap_pilot_d : insert_d,
                     h = (tapped ? tap_depth : insert_depth) + 1);
    }
}

module board_bosses() {
    for (x = [green_hole_inset, green[0] - green_hole_inset],
         y = [green_hole_inset, green[1] - green_hole_inset])
        boss(x, y, wire_space);
    for (y = black_hole_y) boss(black_hole_x, y, wire_space);
}

// The boards drop straight in, so a post anywhere inside their footprint
// blocks them at every height — tapering its foot would not help. The posts
// therefore sit against the outer wall, in the four places the boards leave:
// off both ends, along the back, and across the front only where the narrower
// KY-040 board stops short of it. That leaves one corner, at the seam on the
// front, with no room for an insert's Ø6 boss; it gets a slim tapped one.
// [x, y, tapped]
function fixings(lid) =
    let (front = outer[0][1] + boss_d / 2,
         back = outer[1][1] - boss_d / 2,
         elbow = outer[0][0] + boss_d / 2,
         hand = outer[1][0] - boss_d / 2,
         black_mid = green[0] + black_gap + black[0] / 2)
    lid == "elbow"
        ? [[elbow, front, false], [elbow, back, false],
           [seam_x - boss_d / 2 - 1, back, false],
           [seam_x - tap_boss_d / 2 - 1, outer[0][1] + tap_boss_d / 2, true]]
        : [[seam_x + boss_d / 2 + 1, back, false], [black_mid, front, false],
           [hand, front, false], [hand, back, false]];

module lid_posts() {
    for (lid = ["elbow", "hand"], f = fixings(lid))
        boss(f[0], f[1], top_hand - floor_z, f[2]);
}

module strap_lugs() {
    // The band crosses the arm, so it threads through the long sides. Each lug
    // is a tall plate held off the flank by a post at either end: the band
    // passes up the gap behind it, open top and bottom, and covers the case's
    // height on the way. A tab on the end of the case could not do that — the
    // band would run along the arm instead of around it.
    //
    // The plate runs the full height of the case, down to the same plane the
    // case stands on, so it prints off the bed instead of cantilevering off
    // its posts, and the band cannot slip out under it.
    mid_x = (outer[0][0] + outer[1][0]) / 2;
    z_hi = top_hand + lid_t - strap_lug_drop;
    z_lo = floor_z - floor_t;
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
                hull() for (z = [z_lo + post / 2, z_hi - post / 2])
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
            lid_posts();
            strap_lugs();
        }
        openings();
    }
}

module screw_holes(lid, top) {
    for (f = fixings(lid)) translate([f[0], f[1], top - 1]) {
        cylinder(d = screw_d, h = lid_t + 2);
        translate([0, 0, lid_t + 1 - 1.2]) cylinder(d = screw_head_d, h = 1.4);
    }
}

module lid(x0, x1, top) {
    intersection() {
        shell();
        translate([x0, outer[0][1] - 1, top])
            cube([x1 - x0, size_xy[1] + 2, lid_t]);
    }
}

module lid_hand() {
    difference() {
        lid(seam_x, outer[1][0] + 1, top_hand);
        screw_holes("hand", top_hand);
        for (y = button_y)
            translate([button_x, y, top_hand - 1]) cylinder(d = button_hole_d, h = lid_t + 2);
        translate([shaft[0], shaft[1], top_hand - 1])
            cylinder(d = bush_d + knob_clear, h = lid_t + 2);
    }
}

module lid_elbow() {
    // A raised cap over the screen: walls straight off the base's rim, a roof
    // with the window in it, and the hand end ramping down at 45 degrees so
    // the slope prints without support. It lands on the rim only at four
    // screw tabs — a continuous flange would be a 6 mm ledge all the way round
    // the inside, which is an overhang the printer has to be told about.
    //
    // The screen's glass sits straight against the roof's inner face. Four
    // pins pass through its mounting holes and are flattened with a hot iron;
    // a blob of hot glue instead works just as well.
    pin_len = screen_glass_t + screen_pcb_t + screen_stake;
    difference() {
        union() {
            difference() {
                intersection() {
                    shell();
                    translate([outer[0][0] - 1, outer[0][1] - 1, top_hand])
                        cube([seam_x - outer[0][0] + 1, size_xy[1] + 2,
                              top_screen + lid_t - top_hand]);
                }
                // stop short of the ramp, or the cap loses its hand-end wall
                rounded_block(inner[0],
                              [seam_x - (top_screen - top_hand) - wall, inner[1][1]],
                              top_hand - 1, top_screen, max(corner_r - wall, 1));
            }
            intersection() {
                shell();
                for (f = fixings("elbow"))
                    translate([f[0], f[1], top_hand]) cylinder(d = tab_d, h = lid_t);
            }
            for (p = screen_holes())
                translate([p[0], p[1], top_screen - pin_len])
                    cylinder(d = screen_pin_d, h = pin_len);
        }
        win = [win_hi[0] - win_lo[0], win_hi[1] - win_lo[1]];
        translate([win_lo[0], win_lo[1], top_screen - 1])
            cube([win[0], win[1], lid_t - window_bevel + 1]);
        // the roof is 2 mm of plastic in front of the glass, so the outside of
        // the window flares at 45 degrees to give the edges back their angle
        hull() {
            translate([win_lo[0], win_lo[1], top_screen + lid_t - window_bevel])
                cube([win[0], win[1], 0.01]);
            translate([win_lo[0] - window_bevel, win_lo[1] - window_bevel,
                       top_screen + lid_t - 0.01])
                cube([win[0] + 2 * window_bevel, win[1] + 2 * window_bevel, 1]);
        }
        screw_holes("elbow", top_hand);
        // Sunk into the face, not raised off it: this face prints against the
        // bed, so the letters start a couple of layers up and a filament swap
        // there puts them in their own colour.
        translate([(win_lo[0] + win_hi[0]) / 2, (inner[0][1] + win_lo[1]) / 2,
                   top_screen + lid_t - label_depth])
            linear_extrude(label_depth + 1)
                text(label, size = label_size, font = label_font,
                     halign = "center", valign = "center");
    }
}

function screen_holes() = [
    for (x = [screen_at[0] + screen_hole_inset[0],
              screen_at[0] + screen_pcb[0] - screen_hole_inset[0]],
         y = [screen_at[1] + screen_hole_inset[1],
              screen_at[1] + screen_pcb[1] - screen_hole_inset[1]]) [x, y]
];


module plate() {
    base_w = size_xy[1] + 2 * (strap_gap + strap_bar);
    row2 = base_w + plate_gap;
    cap_len = seam_x - outer[0][0];
    hand_len = outer[1][0] - seam_x;
    used = [max(size_xy[0], hand_len + plate_gap + cap_len), row2 + size_xy[1]];
    assert(used[0] <= bed[0] && used[1] <= bed[1], "plate does not fit one bed");
    echo(str("plate ", used[0], " x ", used[1], " mm"));

    translate([-outer[0][0], -outer[0][1] + strap_gap + strap_bar, -(floor_z - floor_t)])
        base();
    translate([-seam_x, -outer[0][1] + row2, -top_hand])
        lid_hand();
    translate([-outer[0][0] + hand_len + plate_gap, outer[1][1] + row2,
               top_screen + lid_t])
        rotate([180, 0, 0]) lid_elbow();
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
else if (part == "plate") plate();
