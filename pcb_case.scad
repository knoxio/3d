// pcb_case.scad
//
// Parametric PCB case + snap-fit lid for FDM 3D printing.
// All dimensions in millimetres.
//
// ---------- Coordinate system ----------
//
// PCB-coords have origin (0,0) at corner d. pcb_length runs along +X,
// pcb_width along +Y. The four corners of the PCB are:
//
//   d = (0,        0)
//   b = (pcb_length, 0)
//   c = (0,        pcb_width)
//   a = (pcb_length, pcb_width)
//
// Walls of the case are named after the PCB edge they enclose:
//
//   "bd" - wall along the low-Y  edge (between corners b and d)
//   "ac" - wall along the high-Y edge (between corners a and c)
//   "cd" - wall along the low-X  edge (between corners c and d)
//   "ab" - wall along the high-X edge (between corners a and b)
//
// Snap-fit wedges live on the cd/ab walls. Put wall cutouts on the
// bd/ac walls to avoid interfering with the snap mechanism. The module
// assumes pcb_length >= pcb_width (rotate dimensions if your board is
// taller than wide).
//
// ---------- Cutout spec ----------
//
// Each entry in `cutouts` is a 5-element list:
//
//   [wall, low_pos, width, z_above_pcb_top, height]
//
//   wall            - "bd" | "ac" | "cd" | "ab"
//   low_pos         - PCB-coord of the lower-coordinate end of the cutout.
//                     For bd / ac walls this is an X coordinate.
//                     For cd / ab walls this is a Y coordinate.
//   width           - extent of the cutout along the wall direction
//   z_above_pcb_top - vertical offset from the top surface of the PCB
//                     (0 = flush with PCB top)
//   height          - vertical extent of the cutout
//
// ---------- Example ----------
//
//   use <pcb_case.scad>;
//   pcb_case(
//       pcb_length          = 70,
//       pcb_width           = 30,
//       pcb_thickness       = 1.5,
//       pcb_hole_d          = 2.0,
//       pcb_hole_edge_inset = 1.0,
//       bottom_clearance    = 2.4,
//       top_clearance       = 12.0,
//       cutouts = [
//           ["bd", 6,    10, 0,   6  ],   // USB 1, flush with PCB top
//           ["bd", 20.5, 10, 0,   6  ],   // USB 2
//           ["ac", 39,   11, 2.4, 6.5],   // cable cutout, 2.4 mm above PCB
//       ],
//       show = "all"
//   );

module pcb_case(
    // ---- PCB ----
    pcb_length,
    pcb_width,
    pcb_thickness       = 1.6,
    pcb_hole_d          = 2.0,
    pcb_hole_edge_inset = 1.0,             // PCB edge to nearest edge of hole

    // ---- Clearances ----
    bottom_clearance    = 2.5,             // case floor to PCB underside
    top_clearance       = 12.0,            // PCB top to inside of lid
    pcb_side_clearance  = 1.0,             // PCB edge to inside wall

    // ---- Shell ----
    wall_thickness      = 2.0,
    floor_thickness     = 2.0,

    // ---- Standoffs (corner posts that align the PCB) ----
    standoff_shoulder_d = 3.0,             // base supporting the PCB
    standoff_pin_d      = 1.8,             // pin into the PCB hole

    // ---- Lid + snap fit ----
    lid_thickness        = 2.0,
    lid_clearance        = 0.3,            // slip fit between skirt and cavity
    skirt_height         = 5.0,
    skirt_thickness      = 1.5,
    snap_ridge_depth     = 0.4,            // interference depth
    snap_ridge_height    = 1.0,            // ridge extent in Z
    snap_offset_from_top = 1.5,            // case top to top of case ridge
    snap_end_inset       = 3.0,            // pull ridges away from corners

    // ---- PCB hold-down posts on the lid ----
    pcb_hold_down        = true,           // add corner posts that press the PCB down
    corner_post_d        = 4.0,            // outer diameter of each post
    corner_post_relief_d = 2.5,            // bottom relief diameter, clears the standoff pin

    // ---- Wall cutouts (see header for spec) ----
    cutouts              = [],

    // ---- Render selector ----
    //   "base"      - base only
    //   "lid"       - lid only (skirt down)
    //   "assembled" - lid placed on top of base, fully seated
    //   "all"       - base + lid side by side (default)
    show                 = "all",

    // ---- Mesh quality ----
    fn                   = 64
) {
    // ---------- Derived ----------
    pcb_hole_inset = pcb_hole_edge_inset + pcb_hole_d / 2;

    inner_l = pcb_length + 2 * pcb_side_clearance;
    inner_w = pcb_width  + 2 * pcb_side_clearance;
    inner_h = bottom_clearance + pcb_thickness + top_clearance;

    outer_l = inner_l + 2 * wall_thickness;
    outer_w = inner_w + 2 * wall_thickness;
    outer_h = inner_h + floor_thickness;

    pcb_x0  = wall_thickness + pcb_side_clearance;
    pcb_y0  = wall_thickness + pcb_side_clearance;

    pcb_top_z = floor_thickness + bottom_clearance + pcb_thickness;

    case_snap_z_top    = outer_h - snap_offset_from_top;
    case_snap_z_bottom = case_snap_z_top - snap_ridge_height;

    lid_world_offset     = outer_h - skirt_height;
    lid_snap_z_top_local = case_snap_z_bottom - lid_world_offset;
    lid_snap_z_bot_local = lid_snap_z_top_local - snap_ridge_height;

    snap_y_start = wall_thickness + snap_end_inset;
    snap_y_end   = outer_w - wall_thickness - snap_end_inset;
    snap_y_len   = snap_y_end - snap_y_start;

    hole_positions = [
        [pcb_x0 + pcb_hole_inset,                pcb_y0 + pcb_hole_inset],
        [pcb_x0 + pcb_length - pcb_hole_inset,   pcb_y0 + pcb_hole_inset],
        [pcb_x0 + pcb_hole_inset,                pcb_y0 + pcb_width - pcb_hole_inset],
        [pcb_x0 + pcb_length - pcb_hole_inset,   pcb_y0 + pcb_width - pcb_hole_inset],
    ];

    // ---------- Sub-modules ----------

    module _cutout(spec) {
        eps  = 0.1;
        wall = spec[0];
        pos  = spec[1];
        w    = spec[2];
        z_b  = pcb_top_z + spec[3];
        h    = spec[4];

        if (wall == "bd") {
            translate([pcb_x0 + pos, -eps, z_b])
                cube([w, wall_thickness + 2 * eps, h]);
        } else if (wall == "ac") {
            translate([pcb_x0 + pos, outer_w - wall_thickness - eps, z_b])
                cube([w, wall_thickness + 2 * eps, h]);
        } else if (wall == "cd") {
            translate([-eps, pcb_y0 + pos, z_b])
                cube([wall_thickness + 2 * eps, w, h]);
        } else if (wall == "ab") {
            translate([outer_l - wall_thickness - eps, pcb_y0 + pos, z_b])
                cube([wall_thickness + 2 * eps, w, h]);
        }
    }

    module _shell() {
        difference() {
            cube([outer_l, outer_w, outer_h]);
            translate([wall_thickness, wall_thickness, floor_thickness])
                cube([inner_l, inner_w, inner_h + 1]);
            for (c = cutouts) _cutout(c);
        }
    }

    module _standoff() {
        cylinder(h = bottom_clearance, d = standoff_shoulder_d, $fn = fn);
        translate([0, 0, bottom_clearance])
            cylinder(h = pcb_thickness, d = standoff_pin_d, $fn = fn);
    }

    module _standoffs() {
        for (p = hole_positions)
            translate([p[0], p[1], floor_thickness]) _standoff();
    }

    // Wedge cross-section is a right triangle.
    // For the CASE wedges: flat bottom = catch, ramped top = insertion ramp.
    // For the LID  wedges: flat top    = catch, ramped bottom = insertion ramp.

    module _case_snap_wedge_cd() {
        translate([wall_thickness, snap_y_end, case_snap_z_bottom])
            rotate([90, 0, 0])
            linear_extrude(height = snap_y_len)
                polygon([[0, 0],
                         [snap_ridge_depth, 0],
                         [0, snap_ridge_height]]);
    }

    module _case_snap_wedge_ab() {
        translate([outer_l - wall_thickness, snap_y_end, case_snap_z_bottom])
            rotate([90, 0, 0])
            linear_extrude(height = snap_y_len)
                polygon([[0, 0],
                         [-snap_ridge_depth, 0],
                         [0, snap_ridge_height]]);
    }

    module _lid_snap_wedge_cd() {
        translate([wall_thickness + lid_clearance, snap_y_end, lid_snap_z_bot_local])
            rotate([90, 0, 0])
            linear_extrude(height = snap_y_len)
                polygon([[0, snap_ridge_height],
                         [-snap_ridge_depth, snap_ridge_height],
                         [0, 0]]);
    }

    module _lid_snap_wedge_ab() {
        translate([outer_l - wall_thickness - lid_clearance, snap_y_end, lid_snap_z_bot_local])
            rotate([90, 0, 0])
            linear_extrude(height = snap_y_len)
                polygon([[0, snap_ridge_height],
                         [snap_ridge_depth, snap_ridge_height],
                         [0, 0]]);
    }

    // PCB top in lid-local coordinates (skirt bottom = local Z 0)
    pcb_top_local_z = pcb_top_z - lid_world_offset;

    module _lid_corner_post() {
        difference() {
            // post extends from PCB top up to the underside of the lid top plate
            translate([0, 0, pcb_top_local_z])
                cylinder(h = top_clearance, d = corner_post_d, $fn = fn);
            // relief at the bottom to clear the standoff pin
            translate([0, 0, pcb_top_local_z - 0.05])
                cylinder(h = pcb_thickness + 0.1,
                         d = corner_post_relief_d, $fn = fn);
        }
    }

    module _lid() {
        // top plate
        translate([0, 0, skirt_height])
            cube([outer_l, outer_w, lid_thickness]);

        // short-end skirts (cd / ab walls)
        skirt_y_start_  = wall_thickness + lid_clearance;
        skirt_y_end_    = outer_w - wall_thickness - lid_clearance;
        skirt_y_len_    = skirt_y_end_ - skirt_y_start_;

        translate([wall_thickness + lid_clearance, skirt_y_start_, 0])
            cube([skirt_thickness, skirt_y_len_, skirt_height]);

        translate([outer_l - wall_thickness - lid_clearance - skirt_thickness,
                   skirt_y_start_, 0])
            cube([skirt_thickness, skirt_y_len_, skirt_height]);

        _lid_snap_wedge_cd();
        _lid_snap_wedge_ab();

        if (pcb_hold_down) {
            for (p = hole_positions)
                translate([p[0], p[1], 0]) _lid_corner_post();
        }
    }

    module _base() {
        _shell();
        _standoffs();
        _case_snap_wedge_cd();
        _case_snap_wedge_ab();
    }

    // Lid in print orientation: top plate flat on the bed, skirt + posts up.
    module _lid_print_oriented() {
        translate([0, outer_w, skirt_height + lid_thickness])
            rotate([180, 0, 0])
            _lid();
    }

    // ---------- Render ----------
    if      (show == "base")      _base();
    else if (show == "lid")       _lid_print_oriented();
    else if (show == "assembled") { _base(); translate([0, 0, lid_world_offset]) _lid(); }
    else                          { _base(); translate([outer_l + 10, 0, 0]) _lid_print_oriented(); }
}
