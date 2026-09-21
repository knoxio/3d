// ESP project case: 70 x 30 mm PCB with 2 mm corner holes.
//
// Cutouts (on the long bd / ac walls, see pcb_case.scad for the diagram):
//   - Two USB / data cutouts side by side on the bd wall, flush with PCB top.
//   - One cable cutout on the ac wall, 2.4 mm above PCB top.

// parts: base lid

use <../../lib/pcb_case.scad>;

part = "all"; // [all, base, lid, assembled]

pcb_case(
    pcb_length          = 70,
    pcb_width           = 30,
    pcb_thickness       = 1.5,
    pcb_hole_d          = 2.0,
    pcb_hole_edge_inset = 1.0,

    bottom_clearance    = 2.4,
    top_clearance       = 12.0,
    pcb_side_clearance  = 1.0,

    cutouts = [
        // ["wall", low_pos_in_PCB_coords, width, z_above_pcb_top, height]
        ["bd",  6,   10, 0,   6  ],   // 6 mm from d on the bd edge
        ["bd", 20.5, 10, 0,   6  ],   // 4.5 mm after the first cutout
        ["ac", 39,   11, 2.4, 6.5],   // ac wall: 20 mm from a (= 70 - 20 - 11 from c)
    ],

    show = part
);
