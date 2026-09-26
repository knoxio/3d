#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["trimesh", "networkx"]
# ///
# build: manual — needs Blender and the game repo, so CI skips it.
"""Turn the Unspoken game's astronaut into a printable two-part keyring.

The source is a rigged, low-poly, partly open game mesh, so this:

  * swings the arms down (rigidly — the rig's skinning tears the shoulders),
  * widens anything too thin to print, such as the aerials,
  * voxel-remeshes it into one watertight solid,
  * bores a keyring hole below the crown of the helmet,
  * splits the visor off as its own part so it can print in another colour.

Usage: astronaut.py <out_dir> [--height 55] [--src path/to/Astronaut.fbx]

The mesh is third-party (PULSAR BYTES, via the Unity Asset Store). Outputs
stay in the gitignored out/ directory — do not commit them.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

JOB = Path(__file__).with_name("_blender_job.py")
DEFAULT_SRC = Path.home() / (
    "dev/gamedev/ucg/unspoken/Unspoken/Assets/Stylized_Astronaut/Character/Astronaut.fbx"
)

DEFAULTS = {
    "height": 50.0,        # mm, overall figure height
    "arm_drop": 35.0,      # deg, how far the arms swing down from the T-pose
    "arm_insert": 8.0,     # mm the arm root is extruded into the torso before welding
    "min_feature": 1.6,    # mm, thinnest part allowed (the aerials get widened to this)
    "voxel": 0.18,         # mm, remesh resolution
    "visor_material": "Player_Helm",
    "visor_depth": 3.0,    # mm, how deep the visor plug sits in the helmet
    "visor_gap": 0.15,     # mm, clearance around the plug for glue
    "plump": 1.15,         # body only: widen across
    "squash": 0.88,        # body only: compress vertically
    "head_scale": 1.2,     # helmet, scaled uniformly about the neck
    "foot_trim": 1.0,      # mm shaved off the soles so it stands flat
    "keyring_dia": 4.0,    # mm
    "keyring_margin": 3.5, # mm of solid helmet above the hole
    "keyring_stretch": 1.7,  # bore stretched downward into a slot, so a ring can curve through
    "keyring_cone": 1.0,   # mm, lead-in at each mouth
    "split_pack": 1,       # 1 = backpack as its own part, printed lying down
    "pack_tol": 1.5,       # mm, how far in front of the torso's back a pack lump may start
    "pack_centre_frac": 0.3,  # of half-width: how far off centre a pack lump may sit
    "boss_fit": 0.2,       # mm, clearance on the locating cone
    "simplify_angle": 2.0, # deg, merge coplanar triangles below this angle
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("out", type=Path, help="output directory")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="source .fbx")
    for name, value in DEFAULTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=type(value), default=value)
    parser.add_argument(
        "--boss", type=float, nargs=3, default=[6.0, 2.0, 2.0],
        metavar=("BASE", "TIP", "LENGTH"),
        help="mm, locating cone on the backpack joint (45 deg underside)",
    )
    args = parser.parse_args()

    blender = shutil.which("blender")
    if blender is None:
        sys.exit("blender not found on PATH (brew install --cask blender)")
    if not args.src.exists():
        sys.exit(f"source mesh not found: {args.src}")

    cfg = {k: getattr(args, k) for k in DEFAULTS} | {"boss": args.boss}
    cfg |= {"src": str(args.src.resolve()), "out": str(args.out.resolve())}
    result = subprocess.run(
        [blender, "-b", "--python", str(JOB), "--", json.dumps(cfg)],
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("JOB:"):
            print(line[5:])
    # Blender exits 0 even when the script raises, so check the output too
    output = result.stdout + result.stderr
    if result.returncode != 0 or "Error" in output or "Traceback" in output:
        print(result.stdout[-2000:], file=sys.stderr)
        print(result.stderr[-2000:], file=sys.stderr)
        return 1
    return verify(args.out)


def verify(out: Path) -> int:
    """Every part must come out a single watertight solid, or this failed."""
    import trimesh

    bad = 0
    for path in sorted(out.glob("*.stl")):
        mesh = trimesh.load(path)
        mesh.merge_vertices()
        shells = len(mesh.split(only_watertight=False))
        ok = mesh.is_watertight and shells == 1
        size = " x ".join(f"{v:.1f}" for v in mesh.extents)
        print(f"{'ok  ' if ok else 'BAD '} {path.name}: {size} mm, {mesh.volume / 1000:.2f} cm3"
              + ("" if ok else f", watertight={mesh.is_watertight}, {shells} shells"))
        bad += not ok
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
