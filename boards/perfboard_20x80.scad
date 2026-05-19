// Generic case for a 20 x 80 mm perfboard / breadboard PCB (6 x 28 holes).
// Assumes 2 mm corner mounting holes with 1 mm edge inset, like the ESP board.
//
// No wall cutouts defined yet -- add them to the `cutouts` list when you
// know where the USB / wires / buttons need to come out. See pcb_case.scad
// for the wall labels and cutout spec.

use <../pcb_case.scad>;

pcb_case(
    // long axis along X
    pcb_length          = 80,
    pcb_width           = 20,
    pcb_thickness       = 1.5,
    pcb_hole_d          = 2.0,
    pcb_hole_edge_inset = 1.0,

    bottom_clearance    = 2.5,
    top_clearance       = 12.0,
    pcb_side_clearance  = 1.0,

    cutouts = [
        // example: ["bd", 6, 10, 0, 6],
    ],

    show = "all"
);
