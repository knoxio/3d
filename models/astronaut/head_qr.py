#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["trimesh", "networkx", "rtree", "numpy", "manifold3d", "shapely", "svgpathtools", "pillow"]
# ///
# build: manual — requires the owner's helmet STL and QR SVG.
"""Detach the current helmet, preserve its visor fit, and emboss a rear QR.

The original body supplies all surfaces except a narrow region around the
keyring bore. An aligned body rebuilt with --keyring-back 0 supplies that
region. Neither input is scaled. Output coordinates put the visor opening
down and the QR up; the neck cut is perpendicular to the bed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import shutil
import subprocess

import manifold3d as md
import numpy as np
from shapely.geometry import Polygon, MultiPolygon
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from qr_code.build import make_parts, read_artwork, write_plate

REFERENCE_BOUNDS = ((-18.16075325, -10.15826035, 0.0),
                    (18.16075325, 9.48497105, 49.8945694))  # mm, current full body
QR_SIZE = 15.0  # mm, including the four-module quiet zone
QR_MODULE = 14.0  # source SVG units per module
QR_STL_GAP = 0.001  # mm, separates diagonal point contacts at float32 precision
HEAD_X = (-12.230462, 12.042460)  # mm, current helmet envelope before translation
QR_HEIGHT = 0.2  # mm, two black layers
HEAD_DEPTH = 14.0  # mm from the original visor-side extremity to the QR plane
SHOULDER_CUT_Y = -28.0  # mm, limit shoulder trimming to the neck end
ENVELOPE_ALLOWANCE = 0.15  # mm, keep voxel-rounded helmet edges inside the trim envelope
NECK_Y = -24.5  # mm in the rotated, untranslated current 50 mm body frame
QR_CENTRE_Y = -36.47  # mm in that same print frame
QR_CENTRE_X = -0.06  # mm, centred on the available rear facet
BORE_PATCH_GRID = 0.5  # mm, planar patch boundaries outside the six-mm bore
BORE_PATCH_MARGIN = 0.3  # mm beyond the old and new bore sections
MIN_REAR_WALL = 1.7  # mm between the bore and the shaved QR face


@dataclass(frozen=True)
class HeadSettings:
    """Millimetre dimensions in the unscaled, visor-down source frame."""

    neck_y: float = NECK_Y
    shoulder_cut_y: float = SHOULDER_CUT_Y
    neck_planes: tuple[tuple[tuple[float, float, float], float], ...] = ()
    depth: float = HEAD_DEPTH
    qr_size: float = QR_SIZE
    qr_centre_y: float = QR_CENTRE_Y
    qr_centre_x: float = QR_CENTRE_X
    qr_height: float = QR_HEIGHT
    module: float = QR_MODULE
    x_limits: tuple[float, float] | None = HEAD_X


def validate_reference_body(body: trimesh.Trimesh) -> None:
    """Reject rescaled or misaligned bodies against the current printed-visor size."""
    if not np.allclose(body.bounds, REFERENCE_BOUNDS, rtol=0, atol=0.02):
        raise ValueError("Body dimensions differ from the current 50 mm astronaut")


def solid(mesh: trimesh.Trimesh) -> md.Manifold:
    """Convert a closed positive-volume mesh without repairing or rescaling it."""
    if not mesh.is_watertight or mesh.volume <= 0:
        raise ValueError("Input must be a closed positive-volume mesh")
    result = md.Manifold(md.Mesh64(mesh.vertices.astype(np.float64), mesh.faces.astype(np.uint64)))
    if result.status() != md.Error.NoError:
        raise ValueError(f"Manifold rejected mesh: {result.status()}")
    return result


def mesh_of(value: md.Manifold) -> trimesh.Trimesh:
    """Convert an exact solid to an export mesh, retaining its coordinates."""
    data = value.to_mesh64()
    result = trimesh.Trimesh(data.vert_properties[:, :3], data.tri_verts, process=False)
    if not result.is_watertight or result.volume <= 0:
        raise ValueError("Output is not a closed positive-volume mesh")
    return result


def printable_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Quantize to STL precision and discard only collapsed zero-volume debris.

    Float32 export can collapse micrometre-scale boolean triangles. Keep every
    positive-volume component, repair collapsed triangle/quad holes, and reject
    open components or repairs changing volume by more than 0.001 mm³.
    """
    quantized = trimesh.Trimesh(mesh.vertices.astype(np.float32), mesh.faces, process=True)
    pieces = quantized.split(only_watertight=False, repair=True)
    kept = [piece for piece in pieces
            if abs(np.einsum("ij,ij->i", piece.triangles[:, 0],
                             np.cross(piece.triangles[:, 1], piece.triangles[:, 2])).sum() / 6) > 1e-9]
    if not kept or any(not piece.is_watertight or piece.volume <= 0 for piece in kept):
        raise ValueError("STL precision leaves an open or inverted component")
    result = trimesh.util.concatenate(kept)
    if abs(result.volume - mesh.volume) > 0.001:
        raise ValueError("STL cleanup changed physical geometry")
    return result


def visor_rotation(body: trimesh.Trimesh) -> np.ndarray:
    """Align the largest forward-facing pocket floor with the build plate."""
    candidates = [i for i, n in enumerate(body.facets_normal)
                  if n[1] < -0.9 and 0 < n[2] < 0.5 and body.facets_area[i] > 200]
    if not candidates:
        raise ValueError("Cannot identify the current helmet's flat visor pocket")
    normal = body.facets_normal[max(candidates, key=lambda i: body.facets_area[i])]
    z = -normal / np.linalg.norm(normal)
    x = np.array([1.0, 0.0, 0.0])
    x -= np.dot(x, z) * z
    x /= np.linalg.norm(x)
    return np.vstack((x, np.cross(z, x), z))


def bore_section(body: trimesh.Trimesh) -> Polygon:
    """Find the single six-millimetre crown bore in the body's X=0 section."""
    section = body.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
    if section is None:
        raise ValueError("No centre section")
    candidates = []
    for contour in section.discrete:
        extent = np.ptp(contour[:, 1:], axis=0)
        if np.all((extent > 5.7) & (extent < 6.2)) and contour[:, 2].min() > 35:
            polygon = Polygon(contour[:, 1:])
            if polygon.is_valid and 25 < polygon.area < 30:
                candidates.append(polygon)
    if len(candidates) != 1:
        raise ValueError("Expected exactly one current 6 mm crown bore")
    return candidates[0]


def relocate_bore(original: trimesh.Trimesh, forward: trimesh.Trimesh,
                  rotation: np.ndarray) -> tuple[md.Manifold, dict]:
    """Transfer only the local bore region; reject changes near the visor floor.

    Aligned input bounds must match. Everything outside the rectangular crown
    region behind the visor remains the original solid, including the entire visor seat.
    """
    if not np.allclose(original.bounds, forward.bounds, atol=1e-5, rtol=0):
        raise ValueError("Replacement body is not aligned at the original scale")
    old, new = bore_section(original), bore_section(forward)
    delta = np.array(new.centroid.coords[0]) - np.array(old.centroid.coords[0])
    if not (-1.2 < delta[0] < -0.8 and 0 < delta[1] < 2):
        raise ValueError("Replacement must move the bore about 1 mm forward and upward")
    old_diameter = np.subtract(old.bounds[2:], old.bounds[:2])
    new_diameter = np.subtract(new.bounds[2:], new.bounds[:2])
    if np.max(np.abs(old_diameter - new_diameter)) > 0.05:
        raise ValueError("Replacement changes the bore diameter")
    lower = np.floor((np.minimum(old.bounds[:2], new.bounds[:2]) - BORE_PATCH_MARGIN)
                     / BORE_PATCH_GRID) * BORE_PATCH_GRID
    upper = original.bounds[1] + 1
    origin = np.array([original.bounds[0, 0] - 1, *lower])
    patch = md.Manifold.cube(tuple(upper - origin)).translate(tuple(origin))
    original_solid, replacement = solid(original), solid(forward)
    floor_candidates = [i for i, n in enumerate(original.facets_normal)
                        if np.dot(n, -rotation[2]) > 0.999 and original.facets_area[i] > 200]
    floor_triangles = np.concatenate([original.triangles[original.facets[i]]
                                     for i in floor_candidates])
    floor = float(np.max(floor_triangles @ rotation[2]))
    clearance = lower[0] - float(floor_triangles[:, :, 1].max())
    if clearance < 0.5:
        raise ValueError("Bore patch approaches the protected visor pocket")
    result = (original_solid - patch) + (replacement ^ patch)
    change = (result - original_solid) + (original_solid - result)
    if (change - patch).volume() > 1e-6:
        raise ValueError("Bore edit escaped its local patch")
    return result, {"bore_forward_mm": float(-delta[0]), "bore_up_mm": float(delta[1]),
                    "visor_patch_clearance_y_mm": float(clearance),
                    "visor_floor_source_print_z_mm": floor,
                    "bore_diameter_mm": new_diameter.tolist(),
                    "bore_original_section_mm": list(old.bounds),
                    "bore_final_section_mm": list(new.bounds)}


def neck_envelope(body: trimesh.Trimesh, rotation: np.ndarray) -> tuple[tuple[tuple[float, float, float], float], ...]:
    """Extend the four existing lower helmet facets past the shoulder junction.

    Select the largest rear and side facet on each half of the current helmet.
    An outward allowance retains voxel-rounded edges; the cuts apply only at
    the neck, leaving the remainder of the helmet untouched.
    """
    areas, normals, facets = body.facets_area, body.facets_normal, body.facets
    origins, vertices, faces = body.facets_origin, body.vertices, body.faces
    planes = []
    for side in (-1, 1):
        for rear in (False, True):
            candidates = []
            for index in np.flatnonzero((areas > 10) & (normals[:, 2] < -0.3)
                                        & (side * normals[:, 0] > 0.15)):
                normal = normals[index]
                if (normal[1] > 0.5) != rear or normal[1] < 0:
                    continue
                points = vertices[np.unique(faces[facets[index]])]
                if 26 < points[:, 2].mean() < 35:
                    candidates.append(index)
            if not candidates:
                raise ValueError("Cannot identify the current helmet's lower facets")
            index = max(candidates, key=lambda i: areas[i])
            normal = rotation @ normals[index]
            distance = float(normals[index] @ origins[index]) + ENVELOPE_ALLOWANCE
            planes.append((tuple(float(v) for v in normal), distance))
    return tuple(planes)


def shape_head(body: md.Manifold, rotation: np.ndarray, artwork: Polygon | MultiPolygon,
               settings: HeadSettings) -> tuple[trimesh.Trimesh, trimesh.Trimesh, dict]:
    """Make the perpendicular neck cut and QR face, with supported black modules.

    The existing lower helmet facets bound the shoulder removal. Remaining
    helmet surfaces are only rotated, translated or trimmed.
    Only the black artwork must fit on the flat surface. Its four-module
    white quiet zone may continue over the surrounding curved helmet.
    """
    if settings.depth <= 0 or settings.qr_height <= 0:
        raise ValueError("Depth and QR height must be positive")
    value = body.transform(np.column_stack((rotation, np.zeros(3))))
    if settings.neck_y < settings.shoulder_cut_y:
        raise ValueError("Neck plane must follow the shoulder cut")
    value = value.trim_by_plane((0, -1, 0), -settings.neck_y)
    extent = max(abs(v) for v in value.bounding_box()) + 10
    neck_region = md.Manifold.cube((extent * 2,) * 3, center=True).trim_by_plane(
        (0, 1, 0), settings.shoulder_cut_y)
    for normal, distance in settings.neck_planes:
        value -= neck_region.trim_by_plane(normal, distance)
    if settings.x_limits is not None:
        value = value.trim_by_plane((1, 0, 0), settings.x_limits[0])
        value = value.trim_by_plane((-1, 0, 0), -settings.x_limits[1])
    bed_z = value.bounding_box()[2]
    rear_z = bed_z + settings.depth
    value = value.trim_by_plane((0, 0, -1), -rear_z)
    square = md.CrossSection.square((settings.qr_size, settings.qr_size)).translate(
        (settings.qr_centre_x - settings.qr_size / 2, settings.qr_centre_y - settings.qr_size / 2))
    surface = value.slice(rear_z - 0.001)
    outline = md.CrossSection(value.project().to_polygons(), md.FillRule.Positive)
    if (square - outline).area() > 1e-5:
        raise ValueError("The complete QR quiet zone does not fit on the helmet outline")
    black, _ = make_parts(artwork, settings.qr_size, settings.module,
                          face_height=settings.qr_height,
                          thickness=settings.qr_height + 0.1, black_up=True, edge_clearance=QR_STL_GAP)
    black.apply_translation((settings.qr_centre_x - settings.qr_size / 2,
                             settings.qr_centre_y - settings.qr_size / 2, rear_z - 0.1))
    black_outline = solid(black).project()
    if (black_outline - surface).area() > 1e-5:
        raise ValueError("The black QR artwork is not fully supported by the flat face")
    white = printable_mesh(mesh_of(value))
    shift = [-white.bounds[0, 0], -white.bounds[0, 1], -bed_z]
    white.apply_translation(shift)
    black.apply_translation(shift)
    black, white = printable_mesh(black), printable_mesh(white)
    if len(white.split()) != 1:
        raise ValueError("Helmet contains disconnected pieces")
    return black, white, {"rotation": rotation.tolist(), "translation": shift,
                          "white_dimensions_mm": white.extents.tolist(),
                          "qr_size_including_quiet_zone_mm": settings.qr_size,
                          "white_top_z_mm": settings.depth,
                          "black_height_mm": settings.qr_height,
                          "black_artwork_dimensions_mm": black.extents[:2].tolist(),
                          "quiet_zone_surface": "surrounding curved white helmet",
                          "neck_plane_source_y_mm": settings.neck_y}


def preview(destination: Path) -> None:
    """Render depth-tested rear, visor and side views of the exported STL pair."""
    from PIL import Image, ImageDraw, ImageFont

    blender = shutil.which("blender")
    if blender is None:
        raise ValueError("Blender is required for the geometry preview")
    result = subprocess.run([blender, "-b", "--python", str(Path(__file__).with_name("_head_preview.py")),
                             "--", str(destination.parent.resolve())], capture_output=True, text=True)
    if result.returncode or "Traceback" in result.stdout or "Error" in result.stdout:
        raise ValueError(f"Preview render failed: {result.stdout[-1500:]} {result.stderr[-1500:]}")
    canvas = Image.new("RGB", (2700, 970), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=26)
    for index, (name, title) in enumerate([("rear", "QR up / visor on bed"),
                                           ("visor", "Unchanged visor recess"),
                                           ("side", "Moved hole / flat neck")]):
        with Image.open(destination.parent / f"head-{name}.png") as image:
            canvas.paste(image, (index * 900, 70), image)
        draw.text((index * 900 + 450, 28), title, fill="#222222", font=font, anchor="mt")
    canvas.save(destination)


def main() -> None:
    """Export aligned white/black STL parts, a material-assigned 3MF and report."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path)
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--forward-body", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    args = parser.parse_args()
    original = trimesh.load_mesh(args.body)
    validate_reference_body(original)
    forward = trimesh.load_mesh(args.forward_body)
    rotation = visor_rotation(original)
    body, hole_report = relocate_bore(original, forward, rotation)
    black, white, report = shape_head(body, rotation, read_artwork(args.svg), HeadSettings(neck_planes=neck_envelope(original, rotation)))
    new_bore = bore_section(forward)
    points = np.array([[0, y, z] for y, z in new_bore.exterior.coords]) @ rotation.T
    bed = min((original.vertices @ rotation.T)[(original.vertices @ rotation.T)[:, 1] <= NECK_Y, 2])
    wall = bed + HEAD_DEPTH - points[:, 2].max() - 0.1
    front_wall = float(points[:, 2].min() - hole_report["visor_floor_source_print_z_mm"] - 0.1)
    if front_wall < MIN_REAR_WALL:
        raise ValueError(f"Bore leaves only {front_wall:.3f} mm behind the visor pocket")
    if wall < MIN_REAR_WALL:
        raise ValueError(f"QR cut leaves only {wall:.3f} mm behind the keyring bore")
    args.out.mkdir(parents=True, exist_ok=True)
    black.export(args.out / "astronaut-head-qr-black.stl")
    white.export(args.out / "astronaut-head-white.stl")
    write_plate(args.out / "astronaut-head-qr.3mf", [("Astronaut-head-QR", QR_SIZE, black, white)])
    preview(args.out / "astronaut-head-qr.png")
    report |= hole_report | {"rear_bore_wall_lower_bound_mm": float(wall),
                             "front_bore_wall_lower_bound_mm": front_wall,
                             "scale": 1.0,
                             "source_body": str(args.body), "forward_body": str(args.forward_body)}
    (args.out / "geometry-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
