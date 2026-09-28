"""Render the exported head STL pair using Blender's depth-tested renderer."""

from pathlib import Path
import sys

import bpy
from mathutils import Vector

out = Path(sys.argv[sys.argv.index('--') + 1])
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for filename, colour in [('astronaut-head-white.stl', (0.83, 0.83, 0.83, 1)),
                         ('astronaut-head-qr-black.stl', (0.008, 0.008, 0.008, 1))]:
    bpy.ops.wm.stl_import(filepath=str(out / filename))
    obj = bpy.context.object
    obj.color = colour

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'OBJECT'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = False
scene.display.shading.show_specular_highlight = False
scene.display.shading.background_type = 'WORLD'
scene.world.color = (1, 1, 1)
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 37
scene.camera = camera
centre = Vector((12.1, 11.85, 6.4))
for name, offset in [('rear', (30, -38, 75)), ('visor', (30, -38, -75)), ('side', (80, 0, 6))]:
    camera.location = centre + Vector(offset)
    camera.rotation_euler = (centre - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(out / f'head-{name}.png')
    bpy.ops.render.render(write_still=True)
