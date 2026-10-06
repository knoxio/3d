#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
# build: manual — needs the downloaded project, which is not in the repo.
"""Rescale and re-plate the MakerWorld baseball bat for the P1S, with a battery door.

The source is a Bambu Studio project whose five parts were saved at 72 %. This
rewrites each part's placement at the requested scale and lays them out on one
plate. At the designer's size it also swaps the knob for one carrying the
twist-lock socket from knob_end.scad, and adds the cap and the pack sleeve.

Usage: bat.py <out_dir> [--scale 1.0] [--no-door] [--src path/to/V2A1MiniCompatible.3mf]

The model is "Fun Baseball bat - Small printer compatible" by Vulcain
(MakerWorld, CC BY-NC). Download it there; do not commit it or its outputs.
"""

from __future__ import annotations

import argparse
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "V2A1MiniCompatible.3mf"
DOOR = HERE / "knob_end.scad"
MODEL = "3D/3dmodel.model"
RELS = "3D/_rels/3dmodel.model.rels"
SETTINGS = "Metadata/model_settings.config"
KNOB = "V2A1MiniCompatible.stl_3"   # the project's name for the knob piece
BED = 256.0          # mm, P1S plate
MARGIN = 20.0        # mm, clear of the plate's edge and the front-left cutter zone
GAP = 14.0           # mm between parts: two 5 mm brims and some air
MAX_HEIGHT = 245.0   # mm, P1S height with margin

ITEM_RE = re.compile(r'<item objectid="(\d+)"([^>]*?)transform="([^"]+)"')
COMPONENT_RE = re.compile(r'<object id="(\d+)".*?p:path="([^"]+)" objectid="(\d+)"', re.S)
VERTEX_RE = re.compile(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"')
TRIANGLE_RE = re.compile(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"')

Vertex = tuple[float, float, float]
Triangle = tuple[int, int, int]


@dataclass
class Mesh:
    vertices: list[Vertex]
    triangles: list[Triangle]

    def bounds(self) -> tuple[Vertex, Vertex]:
        lo = tuple(min(v[i] for v in self.vertices) for i in range(3))
        hi = tuple(max(v[i] for v in self.vertices) for i in range(3))
        return lo, hi

    def size(self) -> tuple[float, float]:
        """Diameter across and height."""
        lo, hi = self.bounds()
        return max(hi[0] - lo[0], hi[1] - lo[1]), hi[2] - lo[2]

    def moved(self, offset: Vertex) -> Mesh:
        return Mesh([(x + offset[0], y + offset[1], z + offset[2]) for x, y, z in self.vertices],
                    self.triangles)

    def centred(self) -> Mesh:
        """Centre on the origin, which is how the project stores every part."""
        lo, hi = self.bounds()
        return self.moved(tuple(-(lo[i] + hi[i]) / 2 for i in range(3)))


def parse_mesh(model_xml: str) -> Mesh:
    return Mesh([(float(x), float(y), float(z)) for x, y, z in VERTEX_RE.findall(model_xml)],
                [(int(a), int(b), int(c)) for a, b, c in TRIANGLE_RE.findall(model_xml)])


def mesh_xml(object_id: int, mesh: Mesh) -> str:
    # nine digits round-trips a 32-bit float; fewer lets neighbouring vertices coincide
    vertices = "\n".join(f'     <vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>' for x, y, z in mesh.vertices)
    triangles = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.triangles)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="BambuStudio:3mfVersion">1</metadata>
 <resources>
  <object id="{object_id}" p:UUID="{object_id:08x}-81cb-4c03-9d28-80fed5dfa1dc" type="model">
   <mesh>
    <vertices>
{vertices}
    </vertices>
    <triangles>
{triangles}
    </triangles>
   </mesh>
  </object>
 </resources>
 <build/>
</model>
"""


def write_stl(path: Path, mesh: Mesh) -> None:
    with path.open("wb") as f:
        f.write(b"\0" * 80 + struct.pack("<I", len(mesh.triangles)))
        for tri in mesh.triangles:
            f.write(struct.pack("<3f", 0, 0, 0))
            for i in tri:
                f.write(struct.pack("<3f", *mesh.vertices[i]))
            f.write(b"\0\0")


def read_stl(path: Path) -> Mesh:
    """A binary STL, with its repeated corners welded back into shared vertices."""
    data = path.read_bytes()
    (count,) = struct.unpack_from("<I", data, 80)
    index: dict[Vertex, int] = {}
    triangles: list[Triangle] = []
    for n in range(count):
        corners = struct.unpack_from("<9f", data, 84 + n * 50 + 12)
        tri = tuple(index.setdefault(corners[i:i + 3], len(index)) for i in (0, 3, 6))
        if len(set(tri)) == 3:
            triangles.append(tri)
    return Mesh(list(index), triangles)


def door_part(part: str, work: Path, knob_stl: Path) -> Mesh:
    out = work / f"{part}.stl"
    result = subprocess.run(
        ["openscad", "--hardwarnings", "--backend", "manifold", "--export-format", "binstl",
         "-D", f'part="{part}"', "-D", f'knob_mesh="{knob_stl}"', "-o", str(out), str(DOOR)],
        capture_output=True, text=True)
    if result.returncode != 0 or not out.exists():
        sys.exit(f"openscad failed on {part}:\n{result.stderr[-1500:]}")
    return read_stl(out).centred()


def shelf_pack(diameters: dict[int, float]) -> dict[int, tuple[float, float]]:
    """Centre of each part, widest first, in rows across the plate."""
    centres: dict[int, tuple[float, float]] = {}
    x = y = MARGIN
    row_depth = 0.0
    for oid, d in sorted(diameters.items(), key=lambda kv: -kv[1]):
        if x + d > BED - MARGIN:
            x, y, row_depth = MARGIN, y + row_depth + GAP, 0.0
        if y + d > BED - MARGIN:
            sys.exit(f"parts do not fit one {BED:.0f} mm plate at this scale")
        centres[oid] = (x + d / 2, y + d / 2)
        x += d + GAP
        row_depth = max(row_depth, d)
    return centres


def settings_object(object_id: int, part_id: int, name: str, faces: int) -> str:
    return f"""  <object id="{object_id}">
    <metadata key="name" value="{name}"/>
    <metadata key="extruder" value="1"/>
    <metadata face_count="{faces}"/>
    <part id="{part_id}" subtype="normal_part">
      <metadata key="name" value="{name}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <mesh_stat face_count="{faces}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>
    </part>
  </object>
"""


def rebuild(src: Path, out: Path, scale: float, door: bool) -> None:
    with zipfile.ZipFile(src) as zin, tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        model = zin.read(MODEL).decode()
        rels = zin.read(RELS).decode()
        settings = zin.read(SETTINGS).decode()

        # object id in the build -> (file holding its mesh, id inside that file)
        parts = {int(oid): (path.lstrip("/"), int(inner)) for oid, path, inner in COMPONENT_RE.findall(model)}
        meshes = {oid: parse_mesh(zin.read(path).decode()) for oid, (path, _) in parts.items()}
        names = {int(oid): name for oid, name in
                 re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', settings)}
        replaced: dict[str, str] = {}
        added: list[tuple[str, str]] = []

        if door:
            match = re.search(rf'<object id="(\d+)">\s*<metadata key="name" value="{re.escape(KNOB)}"', settings)
            if match is None:
                sys.exit(f"the project has no part named {KNOB}; has the download changed?")
            knob_id = int(match.group(1))
            lo, _ = meshes[knob_id].bounds()
            knob_stl = work / "knob_original.stl"
            write_stl(knob_stl, meshes[knob_id].moved((0, 0, -lo[2])))

            meshes[knob_id] = door_part("knob", work, knob_stl)
            path, inner = parts[knob_id]
            replaced[path] = mesh_xml(inner, meshes[knob_id])
            settings = re.sub(rf'(<object id="{knob_id}">.*?face_count=")\d+(".*?face_count=")\d+',
                              rf"\g<1>{len(meshes[knob_id].triangles)}\g<2>{len(meshes[knob_id].triangles)}",
                              settings, count=1, flags=re.S)

            next_id = max(max(parts), max(inner for _, inner in parts.values())) + 1
            objects = instances = ""
            for part, name in (("cap", "battery cap"), ("sleeve", "battery sleeve")):
                inner, oid, next_id = next_id, next_id + 1, next_id + 2
                mesh = door_part(part, work, knob_stl)
                path = f"3D/Objects/door_{part}.model"
                parts[oid], meshes[oid], names[oid] = (path, inner), mesh, name
                added.append((path, mesh_xml(inner, mesh)))
                objects += (f'  <object id="{oid}" p:UUID="{oid:08x}-61cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
                            f'   <components>\n    <component p:path="/{path}" objectid="{inner}" '
                            f'p:UUID="{inner:08x}-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
                            f'   </components>\n  </object>\n')
                model = model.replace(" </build>", f'  <item objectid="{oid}" p:UUID="{oid:08x}-b1ec-4553-aec9-835e5b724bb4" '
                                      f'transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>\n </build>')
                rels = rels.replace("</Relationships>",
                                    f' <Relationship Target="/{path}" Id="rel-door-{part}" '
                                    f'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>')
                settings = settings.replace("  <plate>", settings_object(oid, inner, name, len(mesh.triangles)) + "  <plate>")
                instances += (f'    <model_instance>\n      <metadata key="object_id" value="{oid}"/>\n'
                              f'      <metadata key="instance_id" value="0"/>\n'
                              f'      <metadata key="identify_id" value="{9000 + oid}"/>\n    </model_instance>\n')
            model = model.replace(" </resources>", objects + " </resources>")
            settings = settings.replace("  </plate>", instances + "  </plate>")

        sizes = {oid: mesh.size() for oid, mesh in meshes.items()}
        tallest = max(h for _, h in sizes.values()) * scale
        if tallest > MAX_HEIGHT:
            sys.exit(f"{tallest:.0f} mm tall at {scale:g}x; the P1S takes {MAX_HEIGHT:.0f}")
        centres = shelf_pack({oid: d * scale for oid, (d, _) in sizes.items()})

        def place(match: re.Match[str]) -> str:
            oid, middle, transform = int(match.group(1)), match.group(2), match.group(3)
            m = [float(v) for v in transform.split()]
            # keep each part's orientation (the tip is stored flipped), drop its old scale
            old = abs(m[8])
            rot = [v / old * scale for v in m[:9]]
            cx, cy = centres[oid]
            cz = sizes[oid][1] * scale / 2
            values = " ".join(f"{v:.9g}" for v in [*rot, cx, cy, cz])
            return f'<item objectid="{oid}"{middle}transform="{values}"'

        model, count = ITEM_RE.subn(place, model)
        if count != len(sizes):
            sys.exit(f"placed {count} of {len(sizes)} parts; the project's layout has changed")

        rewritten = {MODEL: model, RELS: rels, SETTINGS: settings, **replaced}
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = rewritten[info.filename].encode() if info.filename in rewritten else zin.read(info.filename)
                zout.writestr(info, data, zipfile.ZIP_DEFLATED)
            for path, xml in added:
                zout.writestr(path, xml, zipfile.ZIP_DEFLATED)

    for oid, (d, h) in sorted(sizes.items()):
        cx, cy = centres[oid]
        print(f"  part {oid:>2}: Ø{d * scale:5.1f} x {h * scale:5.1f} mm at ({cx:5.1f}, {cy:5.1f})  {names[oid]}")
    print(f"wrote {out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path, help="output directory")
    parser.add_argument("--scale", type=float, default=1.0, help="1.0 is the designer's size")
    parser.add_argument("--no-door", action="store_true", help="leave the knob as downloaded")
    parser.add_argument("--src", type=Path, default=SRC, help="the downloaded project")
    args = parser.parse_args()
    if not args.src.exists():
        sys.exit(f"source project not found: {args.src}")
    door = not args.no_door
    if door and args.scale != 1.0:
        sys.exit("the battery door is drawn for the pack at 1.0x; pass --no-door to scale the bat")
    if door and shutil.which("openscad") is None:
        sys.exit("openscad not found on PATH; it builds the battery door")
    rebuild(args.src, args.out / "bat-p1s.3mf", args.scale, door)
    return 0


if __name__ == "__main__":
    sys.exit(main())
