"""Turn a rounded QR SVG's dot clip path into a face-down, two-material 3MF."""

import argparse
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import manifold3d
from shapely import affinity, make_valid, set_precision
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from svgpathtools import Line, parse_path
import trimesh


SAMPLE_SIZES = (10, 12, 15, 20, 25, 30)


def read_artwork(source: Path) -> Polygon | MultiPolygon:
    """Read filled paths, rectangles and circles from clip-path-dot-color.

    SVG coordinates are retained. Only rotation transforms and even-odd holes
    are supported; unsupported geometry fails instead of silently disappearing.
    """
    root = ET.parse(source).getroot()
    clip = root.find(".//{*}clipPath[@id='clip-path-dot-color']")
    if clip is None:
        raise ValueError("SVG must contain clip-path-dot-color")
    shapes = []
    for element in clip:
        tag = element.tag.split("}")[-1]
        attributes = element.attrib
        if tag == "rect":
            x, y, width, height = (float(attributes[k]) for k in ("x", "y", "width", "height"))
            shape = box(x, y, x + width, y + height)
        elif tag == "circle":
            shape = Point(float(attributes["cx"]), float(attributes["cy"])).buffer(
                float(attributes["r"]), quad_segs=16
            )
        elif tag == "path":
            rings = []
            for subpath in parse_path(attributes["d"]).continuous_subpaths():
                points = []
                for segment in subpath:
                    count = 1 if isinstance(segment, Line) else max(8, math.ceil(segment.length() / 0.7))
                    points.extend((segment.point(t).real, segment.point(t).imag)
                                  for t in np.linspace(0, 1, count, endpoint=False))
                points.append((subpath.end.real, subpath.end.imag))
                rings.append(make_valid(Polygon(points)))
            if len(rings) > 1 and attributes.get("clip-rule") != "evenodd":
                raise ValueError("Multiple rings require explicit evenodd clip-rule")
            shape = rings[0]
            for ring in rings[1:]:
                shape = shape.symmetric_difference(ring)
        else:
            raise ValueError(f"Unsupported SVG element: {tag}")
        transform = attributes.get("transform")
        if transform:
            match = re.fullmatch(r"rotate\(([-\d.]+),([-\d.]+),([-\d.]+)\)", transform)
            if match is None:
                raise ValueError(f"Unsupported transform: {transform}")
            angle, x, y = map(float, match.groups())
            shape = affinity.rotate(shape, angle, origin=(x, y))
        shapes.append(shape)
    result = unary_union([set_precision(shape, 0.000001) for shape in shapes])
    if not isinstance(result, (Polygon, MultiPolygon)) or result.is_empty:
        raise ValueError("Artwork must contain nonempty polygon geometry")
    return result


def face_geometry(artwork: Polygon | MultiPolygon, size: float, module: float) -> Polygon | MultiPolygon:
    """Fit artwork inside four modules of quiet zone, facing the bed.

    SVG Y increases downwards. Retaining that axis makes the bed-facing surface
    read correctly when the printed card is flipped around its horizontal axis.
    """
    if size <= 0 or module <= 0:
        raise ValueError("Size and source module pitch must be positive")
    left, top, right, bottom = artwork.bounds
    if not math.isclose(right - left, bottom - top, abs_tol=0.00001):
        raise ValueError("QR artwork must be square")
    extent = right - left + 8 * module
    shifted = affinity.translate(artwork, xoff=4 * module - left, yoff=4 * module - top)
    return affinity.scale(shifted, xfact=size / extent, yfact=size / extent, origin=(0, 0))


def _extrude(shape, height):
    polygons = [shape] if isinstance(shape, Polygon) else shape.geoms
    contours = []
    for polygon in polygons:
        polygon = orient(polygon, sign=1)
        contours.extend(np.asarray(ring.coords)[:-1] for ring in [polygon.exterior, *polygon.interiors])
    return manifold3d.CrossSection(contours).extrude(height)


def _mesh(solid):
    mesh = solid.to_mesh64()
    return trimesh.Trimesh(vertices=mesh.vert_properties[:, :3], faces=mesh.tri_verts, process=False)


def make_parts(artwork: Polygon | MultiPolygon, size: float, module: float,
               face_height: float = 0.2, thickness: float = 1.2,
               raised: bool = False, black_up: bool = False, edge_clearance: float = 0) -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    """Return closed black and white meshes, optionally leaving recessed gaps.

    Raised mode retains only the quiet-zone border beside the black face.
    The continuous backing starts at face_height and must bridge the gaps.
    Optional edge_clearance shrinks strokes by half that millimetre gap per
    edge, separating diagonal contacts for STL export.
    Black-up mode instead places the QR on a full white base and reverses SVG
    Y so the top reads correctly. The two modes are mutually exclusive.
    """
    if not 0 < face_height < thickness:
        raise ValueError("Face height must be positive and below total thickness")
    if raised and black_up:
        raise ValueError("Raised face-down and black-up modes are mutually exclusive")
    face = face_geometry(artwork, size, module)
    if edge_clearance < 0:
        raise ValueError("Edge clearance cannot be negative")
    if edge_clearance:
        face = face.buffer(-edge_clearance / 2, join_style="mitre")
        if face.is_empty:
            raise ValueError("Edge clearance removes the QR artwork")
    backing = manifold3d.Manifold.cube((size, size, thickness - face_height))
    if black_up:
        face = affinity.scale(face, xfact=1, yfact=-1, origin=(size / 2, size / 2))
        black = _mesh(_extrude(face, face_height).translate((0, 0, thickness - face_height)))
        white = _mesh(backing)
    else:
        black = _mesh(_extrude(face, face_height))
        recess = box(*face.bounds) if raised else face
        white_face = _extrude(box(0, 0, size, size).difference(recess), face_height)
        white = _mesh(white_face + backing.translate((0, 0, face_height)))
    for mesh in (black, white):
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
            raise ValueError("Generated mesh is not a closed positive volume")
    return black, white


def write_plate(destination: Path, samples: list[tuple[str, float, trimesh.Trimesh, trimesh.Trimesh]]) -> None:
    """Write a 3MF with separate black/white parts and up to three columns of six sizes.

    Material 1 is black, material 2 is white. Layout assumes a 256 mm bed and
    reserves the right side for the slicer's purge tower.
    """
    styles = list(dict.fromkeys(style for style, _, _, _ in samples))
    sizes = SAMPLE_SIZES
    if not 1 <= len(styles) <= 3:
        raise ValueError("Plate requires one to three styles")
    if any(size not in sizes for _, size, _, _ in samples):
        raise ValueError("Unsupported sample size")
    if len({(style, size) for style, size, _, _ in samples}) != len(samples):
        raise ValueError("Duplicate style/size would overlap")
    namespace = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", namespace)
    def node(parent, tag, attributes=None):
        return ET.SubElement(parent, f"{{{namespace}}}{tag}", attributes or {})
    root = ET.Element(f"{{{namespace}}}model", {"unit": "millimeter", "{http://www.w3.org/XML/1998/namespace}lang": "en-US"})
    resources = node(root, "resources")
    materials = node(resources, "basematerials", {"id": "100"})
    node(materials, "base", {"name": "Black", "displaycolor": "#000000FF"})
    node(materials, "base", {"name": "White", "displaycolor": "#FFFFFFFF"})
    build = node(root, "build")
    config = ET.Element("config")
    for index, (style, size, black, white) in enumerate(samples):
        parent_id = index * 3 + 3
        settings = ET.SubElement(config, "object", {"id": str(parent_id)})
        name = f"{style} {size:g} mm"
        ET.SubElement(settings, "metadata", {"key": "name", "value": name})
        for color, mesh in enumerate((black, white)):
            object_id = index * 3 + color + 1
            obj = node(resources, "object", {"id": str(object_id), "type": "model", "pid": "100", "pindex": str(color)})
            mesh_node = node(obj, "mesh")
            vertices = node(mesh_node, "vertices")
            for x, y, z in mesh.vertices:
                node(vertices, "vertex", {"x": f"{x:.8f}", "y": f"{y:.8f}", "z": f"{z:.8f}"})
            triangles = node(mesh_node, "triangles")
            for a, b, c in mesh.faces:
                node(triangles, "triangle", {"v1": str(a), "v2": str(b), "v3": str(c)})
            part = ET.SubElement(settings, "part", {"id": str(object_id), "subtype": "normal_part"})
            ET.SubElement(part, "metadata", {"key": "name", "value": "Black QR" if color == 0 else "White backing"})
            ET.SubElement(part, "metadata", {"key": "extruder", "value": str(color + 1)})
        parent = node(resources, "object", {"id": str(parent_id), "type": "model", "name": name})
        components = node(parent, "components")
        for object_id in (index * 3 + 1, index * 3 + 2):
            node(components, "component", {"objectid": str(object_id)})
        row = sizes.index(size)
        x, y = 55 + styles.index(style) * 60 - size / 2, 10 + sum(sizes[:row]) + row * 4
        node(build, "item", {"objectid": str(parent_id), "transform": f"1 0 0 0 1 0 0 0 1 {x} {y} 0"})
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        archive.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        archive.writestr("3D/3dmodel.model", ET.tostring(root, encoding="utf-8", xml_declaration=True))
        archive.writestr("Metadata/model_settings.config", ET.tostring(config, encoding="utf-8", xml_declaration=True))


def main() -> None:
    """Generate the six-size plate and aligned per-size STL pairs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--names", nargs="+")
    parser.add_argument("--module", type=float, default=14, help="Source SVG module pitch")
    parser.add_argument("--thickness", type=float, default=1.2, help="Total thickness including black layers, in mm")
    parser.add_argument("--sizes", type=int, nargs="+", choices=SAMPLE_SIZES, default=SAMPLE_SIZES)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--raised", action="store_true", help="One black layer with recessed internal gaps")
    mode.add_argument("--black-up", action="store_true", help="Two black layers on a continuous white base")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    names = args.names or [source.stem for source in args.svg]
    if len(names) != len(args.svg) or not 1 <= len(names) <= 3 or len(set(names)) != len(names):
        parser.error("Provide one to three SVGs with distinct matching names")
    if any(re.fullmatch(r"[A-Za-z0-9_-]+", name) is None for name in names):
        parser.error("Names may contain letters, numbers, underscores and hyphens")
    samples = []
    for source, name in zip(args.svg, names, strict=True):
        artwork = read_artwork(source)
        for size in args.sizes:
            black, white = make_parts(artwork, size, args.module,
                                      face_height=0.1 if args.raised else 0.2,
                                      thickness=args.thickness, raised=args.raised, black_up=args.black_up)
            for color, mesh in (("black", black), ("white", white)):
                mesh.export(args.output / f"{name}-{size}mm-{color}.stl")
            samples.append((name, size, black, white))
            print(f"{name} {size} mm: both meshes watertight; {black.volume + white.volume:.3f} mm3", flush=True)
    write_plate(args.output / "qr-size-test.3mf", samples)


if __name__ == "__main__":
    main()
