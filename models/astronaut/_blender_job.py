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


def rotate_arms(obj, drop):
    """Rigidly swing each arm down about its shoulder.

    The rig's smooth skinning tears the low-poly shoulder apart, so instead
    every vertex mostly weighted to an arm is rotated as one solid piece. The
    arm root stays buried inside the torso, and the remesh welds it back on.
    The maths is done in world space: the mesh and the armature do not share
    a local frame after an FBX import.
    """
    armature = bpy.data.objects["Armature"]
    to_world = obj.matrix_world
    to_local = to_world.inverted()
    for side, sign in (("Left", 1), ("Right", -1)):
        groups = [obj.vertex_groups[f"Arm_{n}_{side}"].index for n in (1, 2)]
        bone = armature.data.bones[f"Arm_1_{side}"]
        pivot = armature.matrix_world @ bone.head_local
        rot = mathutils.Matrix.Rotation(math.radians(drop) * sign, 4, "Y")
        moved = 0
        for vert in obj.data.vertices:
            weight = sum(g.weight for g in vert.groups if g.group in groups)
            if weight < 0.5:
                continue
            world = to_world @ vert.co
            vert.co = to_local @ (rot @ (world - pivot) + pivot)
            moved += 1
        log(f"arm {side}: rotated {moved} verts by {drop * sign:+.0f} deg")


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
    open_edges = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    bm.to_mesh(obj.data)
    bm.free()
    log(f"cleaned {obj.name}: {len(obj.data.polygons)} tris, {open_edges} open edges")


def keyring_hole(obj, dia, margin):
    """Bore a left-to-right hole near the crown of the helmet.

    Sited `margin` below the top so the bridge above the hole is solid, and
    centred on the helmet's own cross-section rather than the whole figure,
    which is wider at the arms.
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
    bpy.ops.mesh.primitive_cylinder_add(radius=dia / 2, depth=span, location=(cx, cy, z), rotation=(0, math.radians(90), 0))
    drill = bpy.context.active_object
    boolean(obj, drill, "DIFFERENCE")
    bpy.data.objects.remove(drill, do_unlink=True)
    log(f"keyring hole dia {dia} at z {z:.1f} ({margin} below the crown)")


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

rotate_arms(body, cfg["arm_drop"])
for mod in list(body.modifiers):          # drop the armature, the pose is baked in
    body.modifiers.remove(mod)
bpy.data.objects.remove(bpy.data.objects["Armature"], do_unlink=True)

bpy.context.view_layer.update()
scale = cfg["height"] / body.dimensions.z
body.scale = [s * scale for s in body.scale]
bpy.context.view_layer.objects.active = body
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

cutter, visor_normal = visor_cutter(body, cfg["visor_material"], cfg["visor_depth"])
fatten_thin_parts(body, cfg["min_feature"])

remesh(body, cfg["voxel"])

keyring_hole(body, cfg["keyring_dia"], cfg["keyring_margin"])

visor = body.copy()
visor.data = body.data.copy()
bpy.context.collection.objects.link(visor)
visor.name = "visor"
boolean(visor, cutter, "INTERSECT")
boolean(body, cutter, "DIFFERENCE")
bpy.data.objects.remove(cutter, do_unlink=True)
shrink(visor, cfg["visor_gap"])
face_down(visor, visor_normal)
for obj in (body, visor):
    remesh(obj, cfg["voxel"])   # booleans leave slivers; voxels cannot
    simplify(obj, cfg["simplify_angle"])
    clean(obj)

os.makedirs(cfg["out"], exist_ok=True)
for obj, name in ((body, "astronaut-body"), (visor, "astronaut-visor")):
    drop_to_bed(obj)
    export(obj, os.path.join(cfg["out"], f"{name}.stl"))
