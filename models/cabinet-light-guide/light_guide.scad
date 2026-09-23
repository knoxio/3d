// LED strip guide for the crystal cabinet: a shallow channel taped to the
// underside of a shelf/top panel, just behind the front edge. The strip sits
// on a seat tilted toward the back of the cabinet; a front fascia hides it.
//
// Two runs (cabinet top and mid shelf), each 3 pieces: 2 x guide + 1 x
// guide-end. Print with the tape face on the bed; no supports.

// parts: guide guide-end

part = "run"; // [run, guide, guide-end]

/* [Cabinet] */
inner_w = 560;         // mm, clear width between the side panels
side_clear = 2;        // mm, gap at each end
pieces = 3;            // pieces per run

/* [Profile] */
depth = 20;            // mm, front to back
plate_t = 2.4;         // mm, thickness of the plate that takes the tape
fascia_t = 3;          // mm
drop = 15;             // mm, how far the fascia hangs below the panel

/* [Strip seat] */
seat_front = 8;        // mm from the front face
seat_tilt = 11.3;      // deg, aims the strip down and toward the back
seat_z = 6;            // mm below the panel at seat_front
strip_w = 2;           // mm
strip_clear = 0.6;     // mm, total clearance across the strip
rib = [1, 1];          // mm, [width, height] of the retaining ribs

/* [Splice] */
tongue_len = 8;        // mm
tongue_t = 1.2;        // mm, on the tape-face side so it prints flat
tongue_y = [5, 15];    // mm, span across the profile
tongue_fit = 0.2;      // mm, clearance per side

$fa = 2;
$fs = 0.4;

run_len = inner_w - 2 * side_clear;
piece_len = run_len / pieces;
seat_drop = (depth - seat_front) * tan(seat_tilt);
seat_back_z = seat_z - seat_drop;
strip_gap = strip_w + strip_clear;
seat_mid = (seat_front + depth) / 2;

assert(piece_len + tongue_len <= 245, "piece too long for the P1S bed");
assert(seat_back_z > plate_t, "seat runs into the plate; lower seat_tilt");

function seat_z_at(y) = seat_z - (y - seat_front) * tan(seat_tilt);

// Cross-section in (y, z): y from the front face back, z down from the panel.
function profile() = concat(
    [[0, 0], [depth, 0], [depth, seat_back_z]],
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

module run() {
    for (i = [0 : pieces - 1])
        translate([i * piece_len, 0, 0]) color(i % 2 ? "LightSteelBlue" : "SteelBlue")
            piece(i < pieces - 1);
}

if (part == "run") run();
else piece(part == "guide");
