#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
# build: manual — needs the downloaded project, which is not in the repo.
"""Rescale and re-plate the MakerWorld baseball bat for the P1S.

The source is a Bambu Studio project whose five parts were saved at 72 %. This
rewrites each part's placement at the requested scale, lays the parts out on
one plate, and leaves the meshes and print settings untouched.

Usage: bat.py <out_dir> [--scale 1.0] [--src path/to/V2A1MiniCompatible.3mf]

The model is "Fun Baseball bat - Small printer compatible" by Vulcain
(MakerWorld, CC BY-NC). Download it there; do not commit it or its outputs.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

SRC = Path(__file__).with_name("V2A1MiniCompatible.3mf")
MODEL = "3D/3dmodel.model"
BED = 256.0          # mm, P1S plate
MARGIN = 20.0        # mm, clear of the plate's edge and the front-left cutter zone
GAP = 14.0           # mm between parts: two 5 mm brims and some air
MAX_HEIGHT = 245.0   # mm, P1S height with margin

ITEM_RE = re.compile(r'<item objectid="(\d+)"([^>]*?)transform="([^"]+)"')
COMPONENT_RE = re.compile(r'<object id="(\d+)".*?p:path="([^"]+)"', re.S)
VERTEX_RE = re.compile(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"')


def native_size(model_xml: str) -> tuple[float, float]:
    """Diameter across and height of a part's mesh, unscaled."""
    xs, ys, zs = zip(*((float(x), float(y), float(z)) for x, y, z in VERTEX_RE.findall(model_xml)))
    return max(max(xs) - min(xs), max(ys) - min(ys)), max(zs) - min(zs)


def shelf_pack(diameters: dict[str, float]) -> dict[str, tuple[float, float]]:
    """Centre of each part, widest first, in rows across the plate."""
    centres: dict[str, tuple[float, float]] = {}
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


def rescale(src: Path, out: Path, scale: float) -> None:
    with zipfile.ZipFile(src) as zin:
        model = zin.read(MODEL).decode()
        paths = dict(COMPONENT_RE.findall(model))
        sizes = {oid: native_size(zin.read(path.lstrip("/")).decode()) for oid, path in paths.items()}

        tallest = max(h for _, h in sizes.values()) * scale
        if tallest > MAX_HEIGHT:
            sys.exit(f"{tallest:.0f} mm tall at {scale:g}x; the P1S takes {MAX_HEIGHT:.0f}")
        centres = shelf_pack({oid: d * scale for oid, (d, _) in sizes.items()})

        def place(match: re.Match[str]) -> str:
            oid, middle, transform = match.groups()
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

        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = model.encode() if info.filename == MODEL else zin.read(info.filename)
                zout.writestr(info, data, zipfile.ZIP_DEFLATED)

    for oid, (d, h) in sorted(sizes.items(), key=lambda kv: int(kv[0])):
        cx, cy = centres[oid]
        print(f"  part {oid:>2}: Ø{d * scale:5.1f} x {h * scale:5.1f} mm at ({cx:5.1f}, {cy:5.1f})")
    print(f"wrote {out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path, help="output directory")
    parser.add_argument("--scale", type=float, default=1.0, help="1.0 is the designer's size")
    parser.add_argument("--src", type=Path, default=SRC, help="the downloaded project")
    args = parser.parse_args()
    if not args.src.exists():
        sys.exit(f"source project not found: {args.src}")
    rescale(args.src, args.out / "bat-p1s.3mf", args.scale)
    return 0


if __name__ == "__main__":
    sys.exit(main())
