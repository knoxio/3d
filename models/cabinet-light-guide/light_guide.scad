// LED strip guide for the crystal cabinet: a shallow channel taped to the
// underside of a shelf/top panel, just behind the front edge. The strip sits
// on a seat tilted toward the back of the cabinet; a front fascia hides it.
//
// Two runs (cabinet top and mid shelf), each 3 pieces: 2 x guide + 1 x
// guide-end. Print with the tape face on the bed; no supports.

// parts: guide guide-end plate

part = "run"; // [run, guide, guide-end, plate]

/* [Cabinet] */
inner_w = 560;         // mm, clear width between the side panels
side_clear = 2;        // mm, gap at each end
pieces = 3;            // pieces per run

/* [Profile] */
depth = 20;            // mm, front to back
plate_t = 2.4;         // mm, thickness of the plate that takes the tape
fascia_t = 3;          // mm
drop = 16;             // mm, how far the fascia hangs below the panel

/* [Strip seat] */
seat_front = 4;        // mm from the front face
seat_len = 8;          // mm, length of the seat along the profile
seat_tilt = 11.3;      // deg, aims the strip down and toward the back
seat_z = 5;            // mm below the panel at seat_front
strip_w = 2;           // mm
strip_clear = 0.6;     // mm, total clearance across the strip
rib = [1, 1];          // mm, [width, height] of the retaining ribs

/* [Plate] */
bed = [256, 256];      // mm, P1S build plate
plate_gap = 6;         // mm, spacing between pieces on the bed
runs = 2;              // number of runs to lay out

/* [Splice] */
tongue_len = 8;        // mm
tongue_t = 1.2;        // mm, on the tape-face side so it prints flat
tongue_y = [5, 15];    // mm, span across the profile
tongue_fit = 0.2;      // mm, clearance per side

$fa = 2;
$fs = 0.4;

run_len = inner_w - 2 * side_clear;
piece_len = run_len / pieces;
seat_back = seat_front + seat_len;
seat_back_z = seat_z - seat_len * tan(seat_tilt);
strip_gap = strip_w + strip_clear;
seat_mid = seat_front + seat_len / 2;

// Above this angle from horizontal, a viewer below cannot see the strip past
// the fascia. Their eye line to the top shelf is ~48 degrees.
hide_angle = atan((drop - seat_z_at(seat_mid)) / (seat_mid - fascia_t));

assert(piece_len + tongue_len <= 245, "piece too long for the P1S bed");
assert(seat_back_z > plate_t, "seat runs into the plate; shorten seat_len");
assert(hide_angle >= 60, "fascia too shallow to hide the strip at 48 degrees");
echo(str("strip hidden above ", hide_angle, " deg from horizontal"));

function seat_z_at(y) = seat_z - (y - seat_front) * tan(seat_tilt);

// Cross-section in (y, z): y from the front face back, z down from the panel.
function profile() = concat(
    [[0, 0], [depth, 0], [depth, plate_t], [seat_back, plate_t],
     [seat_back, seat_back_z]],
    rib_points(),
    [[seat_front, seat_z], [seat_front, plate_t], [fascia_t, plate_t],
     [fascia_t, drop], [0, drop]]
);

// Ribs either side of the strip channel, walking front-ward along the seat.
function rib_points() = let (
    inner_b = seat_mid + strip_gap / 2,
    outer_b = inner_b + rib[0],
    inner_f = seat_mid - strip_gap / 2,
    outer_f = inner_f - rib[0]
) [
    [outer_b, seat_z_at(outer_b)],
    [outer_b, seat_z_at(outer_b) + rib[1]],
    [inner_b, seat_z_at(inner_b) + rib[1]],
    [inner_b, seat_z_at(inner_b)],
    [inner_f, seat_z_at(inner_f)],
    [inner_f, seat_z_at(inner_f) + rib[1]],
    [outer_f, seat_z_at(outer_f) + rib[1]],
    [outer_f, seat_z_at(outer_f)],
];

module body(len) {
    rotate([90, 0, 90]) linear_extrude(len) polygon(profile());
}

module tongue(c = 0) {
    translate([-0.01, tongue_y[0] - c, -c])
        cube([tongue_len + c, tongue_y[1] - tongue_y[0] + 2 * c, tongue_t + c]);
}

// A piece with a slot at x = 0; `with_tongue` adds the tongue at the far end.
module piece(with_tongue) {
    difference() {
        union() {
            body(piece_len);
            if (with_tongue) translate([piece_len, 0, 0]) tongue();
        }
        tongue(tongue_fit);
    }
}

// Every piece for `runs` runs, laid out side by side on one bed.
module plate() {
    total = runs * pieces;
    width = total * depth + (total - 1) * plate_gap;
    assert(piece_len + tongue_len <= bed[0] && width <= bed[1],
        "pieces do not fit one bed; lower `runs` or split the plate");
    for (i = [0 : total - 1])
        translate([0, i * (depth + plate_gap), 0])
            piece(i % pieces < pieces - 1);
}

module run() {
    for (i = [0 : pieces - 1])
        translate([i * piece_len, 0, 0]) color(i % 2 ? "LightSteelBlue" : "SteelBlue")
            piece(i < pieces - 1);
}

if (part == "run") run();
else if (part == "plate") plate();
else piece(part == "guide");
