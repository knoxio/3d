"""Blender side of the astronaut generator — run by `astronaut.py`, not directly.

Reads a JSON config from the last argv entry: src, out, height, arm_drop,
min_feature, voxel, visor_material, visor_depth, visor_gap.
"""

import json
import math
import os
import sys

import bmesh
import bpy
import mathutils

cfg = json.loads(sys.argv[-1])


def log(*parts):
    print("JOB:", *parts)


def mesh_object():
    return [o for o in bpy.data.objects if o.type == "MESH"][0]


def components(bm):
    """Groups of connected faces."""
    bm.faces.ensure_lookup_table()
    seen, groups = set(), []
    for face in bm.faces:
        if face.index in seen:
            continue
        stack, group = [face], []
        while stack:
            f = stack.pop()
            if f.index in seen:
                continue
            seen.add(f.index)
            group.append(f)
            for edge in f.edges:
                stack.extend(g for g in edge.link_faces if g.index not in seen)
        groups.append(group)
    return groups


def cap_holes(bm):
    """Close every border loop; returns how many edges were left open."""
    for _ in range(3):
        border = [e for e in bm.edges if len(e.link_faces) == 1]
        if not border:
            break
        bmesh.ops.holes_fill(bm, edges=border)
        border = [e for e in bm.edges if len(e.link_faces) == 1]
        if border:
            bmesh.ops.triangle_fill(bm, edges=border, use_beauty=True)
    return sum(1 for e in bm.edges if len(e.link_faces) == 1)


def rotate_arms(obj, drop, insert):
    """Rigidly swing each arm down about its shoulder, with a crisp armpit.

    The rig's smooth skinning tears a 265-triangle shoulder apart, so the arm
    moves as one solid piece, dragging the faces that bridge it to the torso.
    That drag shapes the shoulder, but underneath it sags into a rounded web
    that makes the arm look pinched. Nothing is cut away — cutting leaves
    slots and holes where the arm stands off the torso — instead the arm's
    own underside is extended into the torso as a slab, filling the hollow so
    the weld reads as a sharp crease.
    """
    armature = bpy.data.objects["Armature"]
    to_world, to_local = obj.matrix_world, obj.matrix_world.inverted()
    normal_to_world = obj.matrix_world.to_3x3()
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    weights = bm.verts.layers.deform.active

    for side, sign in (("Left", 1), ("Right", -1)):
        groups = [obj.vertex_groups[f"Arm_{n}_{side}"].index for n in (1, 2)]
        pivot = armature.matrix_world @ armature.data.bones[f"Arm_1_{side}"].head_local
        arm = {v for v in bm.verts if sum(v[weights].get(g, 0) for g in groups) >= 0.5}

        rot = mathutils.Matrix.Rotation(math.radians(drop) * sign, 4, "Y")
        for vert in arm:
            vert.co = to_local @ (rot @ ((to_world @ vert.co) - pivot) + pivot)

        bm.normal_update()
        soles = [
            f for f in bm.faces
            if all(v in arm for v in f.verts)
            and (normal_to_world @ f.normal).normalized().z < -0.4
        ]
        if not soles:
            raise SystemExit(f"no underside face found on the {side} arm")
        copied = [g for g in bmesh.ops.duplicate(bm, geom=soles)["geom"]
                  if isinstance(g, bmesh.types.BMFace)]
        walls = bmesh.ops.extrude_face_region(bm, geom=copied)["geom"]
        for vert in (g for g in walls if isinstance(g, bmesh.types.BMVert)):
            towards = pivot - (to_world @ vert.co)
            vert.co = to_local @ ((to_world @ vert.co)
                                  + towards.normalized() * min(insert, towards.length * 0.9))
        log(f"arm {side}: {drop * sign:+.0f} deg, {len(soles)} underside faces carried "
            f"{insert} mm into the torso")

    bm.to_mesh(obj.data)
    bm.free()


def reproportion(obj, plump, squash, head_scale):
    """Chibi proportions: squat body, bigger head, head shape untouched.

    Widening and squashing the whole figure deforms the helmet into a blob, so
    the two are separated. Body vertices widen across and compress vertically;
    head vertices scale uniformly about the neck, then drop with it, so the
    helmet keeps its shape and just grows against a shorter body.
    """
    armature = bpy.data.objects["Armature"]
    to_world, to_local = obj.matrix_world, obj.matrix_world.inverted()
    group = obj.vertex_groups["Head"].index
    world = [to_world @ v.co for v in obj.data.vertices]
    floor = min(p.z for p in world)
    centre = mathutils.Vector((
        (max(p.x for p in world) + min(p.x for p in world)) / 2,
        (max(p.y for p in world) + min(p.y for p in world)) / 2,
        0,
    ))
    neck = armature.matrix_world @ armature.data.bones["Head"].head_local
    drop = (floor + (neck.z - floor) * squash) - neck.z

    heads = 0
    for vert, point in zip(obj.data.vertices, world):
        if sum(g.weight for g in vert.groups if g.group == group) >= 0.5:
            moved = neck + (point - neck) * head_scale
            moved.z += drop
            heads += 1
        else:
            moved = mathutils.Vector((
                centre.x + (point.x - centre.x) * plump,
                centre.y + (point.y - centre.y) * plump,
                floor + (point.z - floor) * squash,
            ))
        vert.co = to_local @ moved
    log(f"proportions: body x{plump} wide, x{squash} tall; head x{head_scale} ({heads} verts)")


def fatten_thin_parts(obj, min_feature):
    """Widen any component thinner than the nozzle can print (the antennae)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.holes_fill(bm, edges=bm.edges[:])
    widened = []
    for group in components(bm):
        verts = list({v for f in group for v in f.verts})
        for axis in (0, 1):
            lo = min(v.co[axis] for v in verts)
            hi = max(v.co[axis] for v in verts)
            span = hi - lo
            if span >= min_feature:
                continue
            mid = (lo + hi) / 2
            factor = min_feature / max(span, 1e-4)
            for vert in verts:
                vert.co[axis] = mid + (vert.co[axis] - mid) * factor
            widened.append(round(span, 2))
    bm.to_mesh(obj.data)
    bm.free()
    log("widened spans:", widened)


def visor_cutter(obj, material, depth):
    """A slab covering the visor faces, cutting `depth` into the helmet.

    The visor faces are copied out of a duplicate (the original mesh must stay
    whole) and thickened either side of the helmet surface, so the slab always
    reaches through the shell no matter which way the faces point.
    """
    names = [m.name for m in obj.data.materials]
    if material not in names:
        raise SystemExit(f"material {material} not found in {names}")
    index = names.index(material)

    cutter = obj.copy()
    cutter.data = obj.data.copy()
    cutter.name = "visor_cutter"
    bpy.context.collection.objects.link(cutter)

    bm = bmesh.new()
    bm.from_mesh(cutter.data)
    bmesh.ops.delete(
        bm,
        geom=[f for f in bm.faces if f.material_index != index],
        context="FACES",
    )
    if not bm.faces:
        raise SystemExit(f"no faces use {material}")
    normal = sum(((f.normal * f.calc_area()) for f in bm.faces), mathutils.Vector()).normalized()
    bm.to_mesh(cutter.data)
    bm.free()

    solid = cutter.modifiers.new("solid", "SOLIDIFY")
    solid.thickness = depth * 2
    solid.offset = 0.0           # centred on the surface, so it spans the shell
    bpy.context.view_layer.objects.active = cutter
    bpy.ops.object.modifier_apply(modifier="solid")
    log("visor cutter:", len(cutter.data.polygons), "tris, normal", [round(v, 2) for v in normal])
    return cutter, normal


def boolean(target, cutter, operation):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = operation
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="bool")


def remesh(obj, voxel):
    mod = obj.modifiers.new("remesh", "REMESH")
    mod.mode = "VOXEL"
    mod.voxel_size = voxel
    mod.use_smooth_shade = False
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="remesh")


def simplify(obj, angle):
    """Merge the coplanar triangles voxel remeshing leaves on every flat facet."""
    before = len(obj.data.polygons)
    mod = obj.modifiers.new("decimate", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(angle)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="decimate")
    tri = obj.modifiers.new("triangulate", "TRIANGULATE")   # n-gons turn to slivers on STL export
    tri.ngon_method = "BEAUTY"
    tri.quad_method = "BEAUTY"
    bpy.ops.object.modifier_apply(modifier="triangulate")
    log(f"simplified {obj.name}: {before} -> {len(obj.data.polygons)} tris")


def clean(obj):
    """Drop the slivers a boolean leaves behind and close what they opened."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.01)
    bmesh.ops.dissolve_degenerate(bm, dist=0.01, edges=bm.edges[:])
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    extra = []
    for edge in bm.edges:                       # flaps hanging off a non-manifold edge
        if len(edge.link_faces) > 2:
            extra.extend(sorted(edge.link_faces, key=lambda f: f.calc_area())[:-2])
    if extra:
        bmesh.ops.delete(bm, geom=list(set(extra)), context="FACES")
        log(f"dropped {len(set(extra))} non-manifold faces from {obj.name}")
    flat = [f for f in bm.faces if f.calc_area() < 1e-4]   # degenerate, not just small
    if flat:
        bmesh.ops.delete(bm, geom=flat, context="FACES")
        log(f"dropped {len(flat)} zero-area faces from {obj.name}")
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if len(e.link_faces) == 1])
    groups = components(bm)
    slivers = sorted(groups, key=lambda g: sum(f.calc_area() for f in g))[:-1]
    if slivers:
        bmesh.ops.delete(bm, geom=[f for g in slivers for f in g], context="FACES")
        log(f"dropped {len(slivers)} sliver shells from {obj.name}")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # filled holes can be non-planar n-gons, which the STL writer chops into
    # slivers — triangulate here so the exporter has nothing left to decide
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    open_edges = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bm.to_mesh(obj.data)
    bm.free()
    log(f"cleaned {obj.name}: {len(obj.data.polygons)} tris, {open_edges} open edges")
    return open_edges


def make_solid(obj, voxel, angle):
    """Simplify and clean; if that leaves the part open, remesh it and retry."""
    simplify(obj, angle)
    if clean(obj) == 0:
        return
    log(f"{obj.name} still open — remeshing again")
    remesh(obj, voxel)
    simplify(obj, angle)
    if clean(obj) != 0:
        raise SystemExit(f"{obj.name} could not be closed")


def keyring_hole(obj, dia, margin, stretch, cone):
    """Bore a left-to-right keyring slot near the crown of the helmet.

    A round hole through a 16 mm helmet is a tunnel no split ring can curve
    through, so the bore is stretched downward into a slot: the ring finds the
    room it needs below the axis, while `margin` of solid helmet above the hole
    is untouched. Sited on the helmet's own cross-section, not the whole
    figure, which is wider at the arms.
    """
    verts = obj.data.vertices
    top = max(v.co.z for v in verts)
    z = top - margin - dia / 2
    band = [v.co for v in verts if abs(v.co.z - z) < dia]
    if not band:
        raise SystemExit("no geometry at the keyring height")
    cx = (max(p.x for p in band) + min(p.x for p in band)) / 2
    cy = (max(p.y for p in band) + min(p.y for p in band)) / 2
    span = max(obj.dimensions) * 2
    sideways = (0, math.radians(90), 0)

    bpy.ops.mesh.primitive_cylinder_add(radius=dia / 2, depth=span, location=(cx, cy, z), rotation=sideways)
    drill = bpy.context.active_object
    drill.scale = (1, 1, stretch)                      # stretch the bore downward
    drill.location.z -= dia * (stretch - 1) / 2
    bpy.ops.object.transform_apply(location=True, scale=True)
    boolean(obj, drill, "DIFFERENCE")
    bpy.data.objects.remove(drill, do_unlink=True)

    if cone > 0:                                       # small lead-in at each mouth
        half = max(abs(p.x) for p in band)
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cone_add(
                radius1=dia / 2 + cone, radius2=dia / 2, depth=cone,
                location=(cx + side * (half - cone / 2), cy, z),
                rotation=(0, math.radians(-90 * side), 0),
            )
            mouth = bpy.context.active_object
            mouth.scale = (1, 1, stretch)
            mouth.location.z -= dia * (stretch - 1) / 2
            bpy.ops.object.transform_apply(location=True, scale=True)
            boolean(obj, mouth, "DIFFERENCE")
            bpy.data.objects.remove(mouth, do_unlink=True)
    log(f"keyring slot {dia} x {dia * stretch:.1f}, {margin} below the crown")


def flatten_feet(obj, trim):
    """Shave the soles flat.

    The game feet taper to a near-point, so the figure lands on two tiny
    contact patches. Cutting `trim` off the bottom gives it real soles to
    stand on and to stick to the bed.
    """
    if trim <= 0:
        return
    verts = obj.data.vertices
    floor = min(v.co.z for v in verts) + trim
    size = max(obj.dimensions) * 4
    bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, floor - size / 2))
    block = bpy.context.active_object
    boolean(obj, block, "DIFFERENCE")
    bpy.data.objects.remove(block, do_unlink=True)
    log(f"feet: trimmed {trim} mm flat")


def bbox(verts):
    return [(min(v.co[i] for v in verts), max(v.co[i] for v in verts)) for i in range(3)]


def pack_faces(obj, behind_tol, centre_frac):
    """Face indices of the backpack: the lumps sitting behind the torso.

    The torso is the biggest component, so its back face is the divide. Taking
    everything entirely behind it would also grab the two hip pods, which are
    far out to the sides — hence the limit on how far off the centreline a
    component may sit.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    groups = components(bm)
    boxes = [bbox(list({v for f in g for v in f.verts})) for g in groups]
    torso = max(range(len(groups)), key=lambda i: len(groups[i]))
    back = boxes[torso][1][1]
    half_width = max(abs(b[0][i]) for b in boxes for i in (0, 1)) * centre_frac
    chosen = [
        i for i, b in enumerate(boxes)
        if i != torso
        and b[1][0] >= back - behind_tol
        and abs((b[0][0] + b[0][1]) / 2) <= half_width
    ]
    if not chosen:
        raise SystemExit("found nothing behind the torso to make a backpack from")
    faces = {f.index for i in chosen for f in groups[i]}
    log(f"backpack: {len(chosen)} of {len(groups)} components, {len(faces)} faces")
    bm.free()
    return faces


def split_off(obj, face_indices, name):
    """Copy those faces into a new object and delete them from the original."""
    part = obj.copy()
    part.data = obj.data.copy()
    part.name = name
    bpy.context.collection.objects.link(part)
    for target, keep in ((part, True), (obj, False)):
        bm = bmesh.new()
        bm.from_mesh(target.data)
        bm.faces.ensure_lookup_table()
        doomed = [f for f in bm.faces if (f.index in face_indices) != keep]
        bmesh.ops.delete(bm, geom=doomed, context="FACES")
        bm.to_mesh(target.data)
        bm.free()
    return part


def inflate(obj, amount):
    """A copy grown along its normals, to cut a clearance gap with."""
    grown = obj.copy()
    grown.data = obj.data.copy()
    bpy.context.collection.objects.link(grown)
    mod = grown.modifiers.new("inflate", "DISPLACE")
    mod.mid_level = 0.0
    mod.strength = amount
    bpy.context.view_layer.objects.active = grown
    bpy.ops.object.modifier_apply(modifier="inflate")
    return grown


def locating_cone(body, pack, boss, fit):
    """Cone on the torso's back, socket in the pack, so it only glues on true."""
    verts = pack.data.vertices
    cx = (max(v.co.x for v in verts) + min(v.co.x for v in verts)) / 2
    cz = (max(v.co.z for v in verts) + min(v.co.z for v in verts)) / 2
    hit, loc, _, _ = body.ray_cast((cx, max(v.co.y for v in verts) + 10, cz), (0, -1, 0))
    if not hit:
        raise SystemExit("no torso surface behind the backpack for the locating cone")
    base, tip, length = boss
    for obj, operation, grow in ((body, "UNION", 0.0), (pack, "DIFFERENCE", fit)):
        bpy.ops.mesh.primitive_cone_add(
            radius1=base / 2 + grow, radius2=tip / 2 + grow, depth=length + 1,
            location=(cx, loc.y + (length + 1) / 2 - 1, cz),
            rotation=(math.radians(-90), 0, 0),
        )
        cone = bpy.context.active_object
        boolean(obj, cone, operation)
        bpy.data.objects.remove(cone, do_unlink=True)
    log(f"locating cone {base}->{tip} at ({cx:.1f}, {loc.y:.1f}, {cz:.1f})")


def face_down(obj, normal):
    """Lay the visor with its outer face on the bed."""
    obj.data.transform(normal.to_track_quat("-Z", "Y").to_matrix().to_4x4().inverted())


def shrink(obj, gap):
    """Shrink about the centre so the plug drops into its recess with a gap."""
    size = max(obj.dimensions)
    factor = max(1 - 2 * gap / size, 0.5)
    centre = sum((v.co for v in obj.data.vertices), mathutils.Vector()) / len(obj.data.vertices)
    obj.data.transform(
        mathutils.Matrix.Translation(centre)
        @ mathutils.Matrix.Scale(factor, 4)
        @ mathutils.Matrix.Translation(-centre)
    )


def drop_to_bed(obj):
    verts = obj.data.vertices
    offset = mathutils.Vector((
        (max(v.co.x for v in verts) + min(v.co.x for v in verts)) / 2,
        (max(v.co.y for v in verts) + min(v.co.y for v in verts)) / 2,
        min(v.co.z for v in verts),
    ))
    obj.data.transform(mathutils.Matrix.Translation(-offset))
    obj.location = (0, 0, 0)


def export(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True)
    log("wrote", path, [round(v, 1) for v in obj.dimensions], f"{len(obj.data.polygons)} tris")


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=cfg["src"])
body = mesh_object()

rotate_arms(body, cfg["arm_drop"], cfg["arm_insert"])
reproportion(body, cfg["plump"], cfg["squash"], cfg["head_scale"])
for mod in list(body.modifiers):          # drop the armature, the pose is baked in
    body.modifiers.remove(mod)
bpy.data.objects.remove(bpy.data.objects["Armature"], do_unlink=True)

bpy.context.view_layer.update()
scale = (cfg["height"] + cfg["foot_trim"]) / body.dimensions.z   # trim comes off later
body.scale = [s * scale for s in body.scale]
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

cutter, visor_normal = visor_cutter(body, cfg["visor_material"], cfg["visor_depth"])

pack = None
if cfg["split_pack"]:
    pack = split_off(body, pack_faces(body, cfg["pack_tol"], cfg["pack_centre_frac"]), "backpack")

for obj in filter(None, (body, pack)):
    fatten_thin_parts(obj, cfg["min_feature"])
    remesh(obj, cfg["voxel"])

flatten_feet(body, cfg["foot_trim"])
keyring_hole(body, cfg["keyring_dia"], cfg["keyring_margin"], cfg["keyring_stretch"], cfg["keyring_cone"])

if pack is not None:
    spacer = inflate(body, cfg["boss_fit"])      # so the pack sits on the torso, not in it
    boolean(pack, spacer, "DIFFERENCE")
    bpy.data.objects.remove(spacer, do_unlink=True)
    locating_cone(body, pack, cfg["boss"], cfg["boss_fit"])

visor = body.copy()
visor.data = body.data.copy()
bpy.context.collection.objects.link(visor)
visor.name = "visor"
boolean(visor, cutter, "INTERSECT")
boolean(body, cutter, "DIFFERENCE")
bpy.data.objects.remove(cutter, do_unlink=True)
shrink(visor, cfg["visor_gap"])
face_down(visor, visor_normal)

parts = [(body, "astronaut-body"), (visor, "astronaut-visor")]
if pack is not None:
    pack.rotation_euler = (math.radians(90), 0, 0)   # aerials along the bed, not standing
    bpy.ops.object.select_all(action="DESELECT")
    pack.select_set(True)
    bpy.context.view_layer.objects.active = pack
    bpy.ops.object.transform_apply(rotation=True)
    parts.append((pack, "astronaut-backpack"))

for obj, _ in parts:
    make_solid(obj, cfg["voxel"], cfg["simplify_angle"])

os.makedirs(cfg["out"], exist_ok=True)
for obj, name in parts:
    drop_to_bed(obj)
    export(obj, os.path.join(cfg["out"], f"{name}.stl"))
