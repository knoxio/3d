#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Package the chest panel's aligned black and white meshes as one AMS project."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
RELATIONSHIPS = "http://schemas.openxmlformats.org/package/2006/relationships"
MODEL_RELATIONSHIP = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
PROFILE_SOURCE = Path(__file__).with_name("_project_settings.json")
BASE_HEIGHT = 1.2  # mm
DETAIL_HEIGHT = 0.6  # mm
PANEL_WIDTH = 208  # mm
PANEL_HEIGHT = 80  # mm
PLATE_CENTER = 128  # mm


def _node(parent: ET.Element, name: str, attributes: dict[str, str] | None = None) -> ET.Element:
    return ET.SubElement(parent, f"{{{CORE}}}{name}", attributes or {})


def _read_mesh(path: Path, lower: float, upper: float) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("3D/3dmodel.model"))
    if root.get("unit") != "millimeter":
        raise ValueError(f"{path.name}: source units must be millimeters")
    objects = root.findall(f"{{{CORE}}}resources/{{{CORE}}}object")
    if len(objects) != 1:
        raise ValueError(f"{path.name}: expected one mesh object")
    items = root.findall(f"{{{CORE}}}build/{{{CORE}}}item")
    if len(items) != 1 or items[0].get("objectid") != objects[0].get("id") or items[0].get("transform") not in (
        None, "1 0 0 0 1 0 0 0 1 0 0 0"
    ):
        raise ValueError(f"{path.name}: source transform must be identity")
    mesh = objects[0].find(f"{{{CORE}}}mesh")
    if mesh is None:
        raise ValueError(f"{path.name}: mesh is missing")
    vertices_node = mesh.find(f"{{{CORE}}}vertices")
    triangles_node = mesh.find(f"{{{CORE}}}triangles")
    if vertices_node is None or triangles_node is None:
        raise ValueError(f"{path.name}: mesh vertices or triangles are missing")
    vertices = [dict(vertex.attrib) for vertex in vertices_node]
    triangles = [dict(triangle.attrib) for triangle in triangles_node]
    if not vertices or not triangles:
        raise ValueError(f"{path.name}: mesh is empty")
    for vertex in vertices:
        if set(vertex) != {"x", "y", "z"} or not all(
            math.isfinite(float(vertex[axis])) for axis in ("x", "y", "z")
        ):
            raise ValueError(f"{path.name}: invalid vertex")
    for triangle in triangles:
        if set(triangle) != {"v1", "v2", "v3"} or any(
            not 0 <= int(triangle[index]) < len(vertices) for index in ("v1", "v2", "v3")
        ):
            raise ValueError(f"{path.name}: invalid triangle")
    z_values = [float(vertex["z"]) for vertex in vertices]
    if not math.isclose(min(z_values), lower, abs_tol=0.001) or not math.isclose(
        max(z_values), upper, abs_tol=0.001
    ):
        raise ValueError(f"{path.name}: expected Z bounds {lower:g}–{upper:g} mm")
    x_values = [float(vertex["x"]) for vertex in vertices]
    y_values = [float(vertex["y"]) for vertex in vertices]
    if min(x_values) < -PANEL_WIDTH / 2 - 0.001 or max(x_values) > PANEL_WIDTH / 2 + 0.001 or (
        min(y_values) < -PANEL_HEIGHT / 2 - 0.001 or max(y_values) > PANEL_HEIGHT / 2 + 0.001
    ):
        raise ValueError(f"{path.name}: mesh exceeds the panel envelope")
    return vertices, triangles


def write_project(output_dir: Path) -> Path:
    """Write one assembled two-filament 3MF from the OpenSCAD exports in output_dir.

    The detail mesh must already occupy Z=1.2–1.8 mm; no individual part is
    dropped to the build plate or translated relative to its backing.
    """
    parts = [
        ("Black backing", output_dir / "chest_panel-base.3mf", 0, BASE_HEIGHT),
        ("White ornament", output_dir / "chest_panel-detailing.3mf", BASE_HEIGHT, BASE_HEIGHT + DETAIL_HEIGHT),
    ]
    meshes = [(name, _read_mesh(path, lower, upper)) for name, path, lower, upper in parts]

    ET.register_namespace("", CORE)
    root = ET.Element(f"{{{CORE}}}model", {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "en-US"})
    for key, value in (("Application", "BambuStudio-02.08.02.61"), ("BambuStudio:3mfVersion", "1")):
        metadata = _node(root, "metadata", {"name": key})
        metadata.text = value
    resources = _node(root, "resources")
    materials = _node(resources, "basematerials", {"id": "10"})
    _node(materials, "base", {"name": "Black PLA", "displaycolor": "#111111FF"})
    _node(materials, "base", {"name": "White PLA", "displaycolor": "#FFFFFFFF"})
    settings = ET.Element("config")
    setting_object = ET.SubElement(settings, "object", {"id": "3"})
    ET.SubElement(setting_object, "metadata", {"key": "name", "value": "Suspender chest panel"})
    ET.SubElement(setting_object, "metadata", {"key": "extruder", "value": "1"})

    for material_index, (name, (vertices, triangles)) in enumerate(meshes):
        identifier = str(material_index + 1)
        obj = _node(resources, "object", {"id": identifier, "type": "model", "name": name, "pid": "10", "pindex": str(material_index)})
        mesh_node = _node(obj, "mesh")
        vertex_node = _node(mesh_node, "vertices")
        for vertex in vertices:
            _node(vertex_node, "vertex", vertex)
        triangle_node = _node(mesh_node, "triangles")
        for triangle in triangles:
            _node(triangle_node, "triangle", triangle)
        part = ET.SubElement(setting_object, "part", {"id": identifier, "subtype": "normal_part"})
        ET.SubElement(part, "metadata", {"key": "name", "value": name})
        ET.SubElement(part, "metadata", {"key": "extruder", "value": str(material_index + 1)})

    plate = ET.SubElement(settings, "plate")
    ET.SubElement(plate, "metadata", {"key": "plater_id", "value": "1"})
    instance = ET.SubElement(plate, "model_instance")
    ET.SubElement(instance, "metadata", {"key": "object_id", "value": "3"})
    ET.SubElement(instance, "metadata", {"key": "instance_id", "value": "0"})

    assembly = _node(resources, "object", {"id": "3", "type": "model", "name": "Suspender chest panel"})
    components = _node(assembly, "components")
    for identifier in ("1", "2"):
        _node(components, "component", {"objectid": identifier})
    build = _node(root, "build")
    _node(build, "item", {"objectid": "3", "transform": f"1 0 0 0 1 0 0 0 1 {PLATE_CENTER} {PLATE_CENTER} 0"})

    model_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    ET.register_namespace("", TYPES)
    content_types = ET.Element(f"{{{TYPES}}}Types")
    ET.SubElement(content_types, f"{{{TYPES}}}Default", {"Extension": "rels", "ContentType": "application/vnd.openxmlformats-package.relationships+xml"})
    ET.SubElement(content_types, f"{{{TYPES}}}Default", {"Extension": "model", "ContentType": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml"})
    types_xml = ET.tostring(content_types, encoding="utf-8", xml_declaration=True)
    ET.register_namespace("", RELATIONSHIPS)
    relationships = ET.Element(f"{{{RELATIONSHIPS}}}Relationships")
    ET.SubElement(relationships, f"{{{RELATIONSHIPS}}}Relationship", {"Target": "/3D/3dmodel.model", "Id": "rel0", "Type": MODEL_RELATIONSHIP})
    relationships_xml = ET.tostring(relationships, encoding="utf-8", xml_declaration=True)

    destination = output_dir / "chest_panel-project.3mf"
    profile = json.loads(PROFILE_SOURCE.read_text())
    if profile["nozzle_diameter"] != ["0.2"] or profile["filament_colour"] != ["#000000", "#FFFFFF"]:
        raise ValueError("Project profile must specify the 0.2 mm nozzle and black/white filament slots")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", types_xml)
        archive.writestr("_rels/.rels", relationships_xml)
        archive.writestr("3D/3dmodel.model", model_xml)
        archive.writestr("Metadata/model_settings.config", ET.tostring(settings, encoding="utf-8", xml_declaration=True))
        archive.writestr("Metadata/project_settings.config", json.dumps(profile, indent=2, sort_keys=True))
    return destination


def main() -> None:
    """Package the OpenSCAD outputs supplied by the repository build runner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    arguments = parser.parse_args()
    print(write_project(arguments.output_dir))


if __name__ == "__main__":
    main()
