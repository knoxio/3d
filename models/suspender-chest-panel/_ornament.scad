art_canvas_width = 200; // mm, drawing coordinate system
art_canvas_height = 80; // mm, drawing coordinate system
art_curve_steps = 24; // samples per cubic Bezier
art_foliage_drop = 3; // mm below stag, before artwork scaling
art_stem_width = 1.7; // mm before artwork scaling
art_leaf_outline = 1.4; // mm before artwork scaling
art_antler_width = 1.7; // mm before artwork scaling
art_near_leg_width = 3; // mm before artwork scaling
art_far_leg_width = 2.8; // mm before artwork scaling
art_front_leg_width = 3.2; // mm before artwork scaling
art_eye_radius = 0.9; // mm before artwork scaling

function _bezier(points) = [for (i = [0:art_curve_steps])
    let(t = i / art_curve_steps, u = 1 - t)
    u*u*u*points[0] + 3*u*u*t*points[1] + 3*u*t*t*points[2] + t*t*t*points[3]];

function _curves(segments) = [for (segment = segments) each _bezier(segment)];

module _rounded_stroke(points, width) {
    for (i = [0:len(points)-2])
        hull() {
            translate(points[i]) circle(d = width);
            translate(points[i+1]) circle(d = width);
        }
}

module _leaf(root, tip, fullness) {
    axis = tip - root;
    normal = [-axis[1], axis[0]] / norm(axis);
    middle = root + axis / 2;
    outline = _curves([
        [root, root + axis / 3 + normal * fullness,
         middle + normal * fullness, tip],
        [tip, middle - normal * fullness,
         root + axis / 3 - normal * fullness, root]
    ]);
    difference() {
        polygon(outline);
        offset(delta = -art_leaf_outline) polygon(outline);
    }
}

module _foliage_half() {
    _rounded_stroke(_curves([
        [[100,72],[89,61],[79,56],[65,57]],
        [[65,57],[46,58],[28,44],[15,28]]
    ]), art_stem_width);
    _rounded_stroke(_curves([
        [[67,57],[54,48],[51,36],[39,27]]
    ]), art_stem_width);
    _rounded_stroke(_curves([
        [[45,51],[34,50],[23,48],[13,42]]
    ]), art_stem_width);
    _leaf([20,34], [10,23], 3.5);
    _leaf([27,41], [29,27], 3.5);
    _leaf([36,47], [23,43], 3.5);
    _leaf([43,52], [31,59], 3.7);
    _leaf([54,56], [43,64], 3.7);
    _leaf([66,57], [57,65], 3.7);
    _leaf([59,52], [65,41], 3.5);
    _leaf([51,43], [43,34], 3.5);
    _leaf([45,35], [47,23], 3.5);
    _leaf([39,27], [30,19], 3.5);
}

module _stag() {
    difference() {
        union() {
            polygon(_curves([
                [[78,44],[82,38],[91,39],[99,42]],
                [[99,42],[104,40],[104,33],[108,28]],
                [[108,28],[110,25],[111,23],[115,23]],
                [[115,23],[119,23],[119,25],[124,26]],
                [[124,26],[124,28],[121,29],[117,29]],
                [[117,29],[113,33],[112,38],[113,43]],
                [[113,43],[112,47],[108,49],[102,49]],
                [[102,49],[95,51],[89,47],[82,48]],
                [[82,48],[80,48],[78,47],[78,44]]
            ]));
            polygon(_curves([
                [[111,25],[108,22],[108,19],[108,18]],
                [[108,18],[112,19],[114,21],[114,24]],
                [[114,24],[113,25],[112,25],[111,25]]
            ]));
            polygon(_curves([
                [[80,43],[76,42],[74,39],[74,35]],
                [[74,35],[78,36],[80,39],[83,42]],
                [[83,42],[82,43],[81,44],[80,43]]
            ]));
            _rounded_stroke(_curves([
                [[85,46],[84,50],[83,53],[80,56]],
                [[80,56],[78,57],[75,57],[73,57]]
            ]), art_near_leg_width);
            _rounded_stroke(_curves([
                [[90,47],[91,52],[90,56],[88,60]],
                [[88,60],[87,63],[84,65],[83,67]]
            ]), art_near_leg_width);
            _rounded_stroke(_curves([
                [[104,47],[104,52],[103,55],[102,57]],
                [[102,57],[102,61],[104,64],[105,66]]
            ]), art_far_leg_width);
            _rounded_stroke(_curves([
                [[109,45],[109,51],[111,55],[111,58]],
                [[111,58],[110,62],[110,66],[110,68]]
            ]), art_front_leg_width);
            polygon([[81,65],[85,65],[84,68],[80,68]]);
            polygon([[103,65],[106,65],[108,68],[104,68]]);
            polygon([[108,66],[112,66],[112,69],[108,69]]);
        }
        translate([116,25.7]) circle(r = art_eye_radius);
    }
    _rounded_stroke(_curves([
        [[112,24],[108,18],[107,12],[108,5]],
        [[108,5],[108,4],[109,3],[110,2]]
    ]), art_antler_width);
    _rounded_stroke(_curves([
        [[108,13],[113,11],[117,8],[119,4]]
    ]), art_antler_width);
    _rounded_stroke(_curves([
        [[108,10],[103,9],[101,6],[100,4]]
    ]), art_antler_width);
    _rounded_stroke(_curves([
        [[112,24],[118,22],[122,17],[124,11]]
    ]), art_antler_width);
    _rounded_stroke(_curves([
        [[119,21],[124,22],[128,20],[130,17]]
    ]), art_antler_width);
    _rounded_stroke(_curves([
        [[121,18],[118,17],[118,14],[118,12]]
    ]), art_antler_width);
}

/** Original stag and leaf embroidery in a centred 200 × 80 mm drawing canvas. */
module ornament() {
    translate([-art_canvas_width/2, art_canvas_height/2])
        scale([1,-1])
            union() {
                translate([0,art_foliage_drop]) _foliage_half();
                translate([art_canvas_width,art_foliage_drop]) mirror([1,0]) _foliage_half();
                _stag();
            }
}
