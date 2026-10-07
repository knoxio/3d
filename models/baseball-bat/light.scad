// Light core and diffuser for the bat's honeycomb barrel.
//
// Three runs of 60/m WS2812B at 120 degrees on a triangular spine, inside a
// thin printed tube. The spine puts the strips about 5 mm off the axis and the
// tube's wall is 26 mm further out, so a 16.7 mm LED pitch has more than its
// own spacing in which to blend. That distance, not LED density, is what makes
// the hexagons glow evenly rather than showing dots.
//
// It cannot go in after the bat is built: the passages through the handle
// joints are Ø30.6. The core and diffuser are installed as the barrel and tip
// are glued, and the battery lead comes up the spine from the knob.
//
// Four pieces per lit section: a spine, a diffuser tube, and a spider at each
// end. The spiders are separate because they have to reach the bat's bore to
// centre everything, and nothing that wide can pass through the tube — so the
// tube slides onto the spine first and the spiders cap it.
//
// Z runs up the bat, 0 at the bottom of whichever section this is.

// parts: spine-barrel spine-tip diffuser-barrel diffuser-tip spider sample

part = "assembly"; // [assembly, spine-barrel, spine-tip, diffuser-barrel, diffuser-tip, spider, sample]

/* [The bat, measured off the mesh] */
bore_r = 36.75;         // mm, barrel and tip
nail_depth = 2.4;       // mm a barbed nail reaches past the inner face
barrel_len = 180;       // mm
tip_len = 150;          // mm
end_margin = 2;         // mm the assembly stops short of a section's ends

/* [Strip: 60/m WS2812B] */
strip_w = 10;           // mm
strip_t = 1.6;          // mm with its adhesive
runs = 3;

/* [Spine] */
side = 14;              // mm, each face of the triangle: the strip plus margin
spine_wall = 1.4;       // mm
wire_d = 5;             // mm, the lead from the battery runs inside the spine

/* [Diffuser] */
diff_od = 66;           // mm
diff_wall = 0.8;        // mm, two perimeters of a 0.4 nozzle
diff_fit = 0.25;        // mm per side, over the spiders' collars

/* [Spider] */
fins = 3;
fin_t = 1.8;            // mm
fin_len = 6;            // mm it stands clear of the diffuser's end
collar_h = 9;           // mm of spigot inside the diffuser
socket_h = 11;          // mm of the spine it grips
socket_fit = 0.25;      // mm per side
bore_clear = 0.55;      // mm per side, fin tip to the bat's bore

/* [Sample] */
sample_len = 70;        // mm, enough to judge the glow before committing hours

$fa = 2;
$fs = 0.4;

inradius = side / (2 * sqrt(3));
circumradius = side / sqrt(3);
diff_id = diff_od - 2 * diff_wall;
collar_r = diff_id / 2 - diff_fit;
fin_r = bore_r - bore_clear;

function assembly_len(section) = section - 2 * end_margin;
function tube_len(section) = assembly_len(section) - 2 * fin_len;

assert(diff_od / 2 < bore_r - nail_depth - 1,
       "the diffuser fouls the nails standing proud inside the bore");
assert(side - strip_w >= 3, "no margin either side of the strip on the spine");
assert(collar_r + 1 < fin_r, "the collar leaves the fins nothing to reach the bore with");
assert(circumradius + socket_fit + 1.4 < collar_r, "the socket runs into the collar");
assert(socket_h <= fin_len + collar_h, "the hub stands proud of the collar");

echo(str("strip to diffuser ", diff_id / 2 - (inradius + strip_t), " mm, against a 16.7 mm LED pitch"));
echo(str(runs, " runs over ", assembly_len(barrel_len) + assembly_len(tip_len),
         " mm carry ", round(runs * (assembly_len(barrel_len) + assembly_len(tip_len)) * 60 / 1000),
         " LEDs: ", round(runs * (assembly_len(barrel_len) + assembly_len(tip_len)) * 60 / 1000) * 0.06,
         " A all white, about a fifth of that in use"));

module triangle(r, h) { linear_extrude(h) circle(r = r, $fn = 3); }

module spine(len) {
    difference() {
        triangle(circumradius, len);
        translate([0, 0, -0.5]) triangle(circumradius - spine_wall * 2 / sqrt(3), len + 1);
        // the lead leaves the spine at either end, whichever way up it goes in
        for (z = [socket_h + 6, len - socket_h - 6]) translate([0, 0, z])
            rotate([0, 90, 0]) cylinder(d = wire_d, h = side, center = true);
    }
}

// Webs in two tiers: out to the bat's bore for the first few millimetres, then
// pulled back inside the collar so the diffuser can slide over them. Radial
// either way, so they print as upright walls rather than as ledges.
module spider() {
    hub_r = circumradius + socket_fit + 1.4;
    difference() {
        union() {
            difference() {      // the collar, a ring the diffuser slides onto
                translate([0, 0, fin_len]) cylinder(r = collar_r, h = collar_h);
                translate([0, 0, fin_len - 0.5])
                    cylinder(r = collar_r - 1.2, h = collar_h + 1);
            }
            cylinder(r = hub_r, h = socket_h);
            for (k = [0 : fins - 1]) rotate([0, 0, 30 + k * 360 / fins]) {
                translate([0, -fin_t / 2, 0]) cube([fin_r, fin_t, fin_len]);
                translate([0, -fin_t / 2, fin_len]) cube([collar_r, fin_t, collar_h]);
            }
        }
        translate([0, 0, -0.5]) triangle(circumradius + socket_fit, socket_h + 0.5);
    }
}

module diffuser(len) {
    difference() {
        cylinder(d = diff_od, h = len);
        translate([0, 0, -0.5]) cylinder(d = diff_id, h = len + 1);
    }
}

module strips(len) {
    for (k = [0 : runs - 1]) rotate([0, 0, k * 360 / runs])
        translate([-strip_w / 2, inradius, 8]) cube([strip_w, strip_t, len - 16]);
}

module lit(len) {
    color("Gainsboro") spine(len);
    color("Silver") spider();
    color("Silver") translate([0, 0, len]) mirror([0, 0, 1]) spider();
    color("Cyan", 0.22) translate([0, 0, fin_len]) diffuser(len - 2 * fin_len);
    color("ForestGreen") strips(len);
}

if (part == "spine-barrel") spine(assembly_len(barrel_len));
else if (part == "spine-tip") spine(assembly_len(tip_len));
else if (part == "diffuser-barrel") diffuser(tube_len(barrel_len));
else if (part == "diffuser-tip") diffuser(tube_len(tip_len));
else if (part == "spider") spider();
else if (part == "sample") {
    spine(sample_len);
    translate([diff_od + 10, 0, 0]) diffuser(sample_len - 2 * fin_len);
    translate([0, diff_od + 10, 0]) spider();
    translate([diff_od + 10, diff_od + 10, 0]) spider();
}
else {
    lit(assembly_len(barrel_len));
    color("Peru", 0.10) difference() {
        cylinder(r = bore_r + 2.54, h = barrel_len);
        translate([0, 0, -1]) cylinder(r = bore_r, h = barrel_len + 2);
    }
}
