#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Build printable files for every model under models/.

OpenSCAD sources (`models/<slug>/<name>.scad`) export to
`out/<slug>/<name>[-<part>].<fmt>` plus a PNG preview. A `// parts: a b c`
header line exports one file per part, passing `-D part="<name>"`.

Python generators (`models/<slug>/<name>.py`) run with `uv run <file> <outdir>`
and must write their own files into `<outdir>`.

Files whose name starts with `_` are treated as includes and skipped.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
OUT = ROOT / "out"
PARTS_RE = re.compile(r"^\s*//\s*parts:\s*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Job:
    source: Path
    part: str | None

    @property
    def stem(self) -> str:
        return f"{self.source.stem}-{self.part}" if self.part else self.source.stem


def discover(selected: list[str]) -> list[Path]:
    sources = sorted(
        p
        for p in MODELS.rglob("*")
        if p.suffix in {".scad", ".py"} and not p.name.startswith("_")
    )
    if not selected:
        return sources
    wanted = [s.strip("/") for s in selected]
    picked = [
        p
        for p in sources
        if any(
            p.parent.relative_to(MODELS).as_posix() == w
            or p.relative_to(MODELS).as_posix() == w
            for w in wanted
        )
    ]
    if not picked:
        sys.exit(f"no models match: {', '.join(selected)}")
    return picked


def scad_jobs(source: Path) -> list[Job]:
    match = PARTS_RE.search(source.read_text())
    if not match:
        return [Job(source, None)]
    return [Job(source, part) for part in match.group(1).split()]


def openscad(job: Job, target: Path, extra: list[str]) -> None:
    cmd = ["openscad", "--hardwarnings", "--backend", "manifold", "-o", str(target)]
    if job.part:
        cmd += ["-D", f'part="{job.part}"']
    cmd += [*extra, str(job.source)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{job.source.relative_to(ROOT)} [{job.part or '-'}]\n{result.stderr}")


def build_scad(source: Path, dest: Path, fmt: str, preview: bool) -> list[Path]:
    written: list[Path] = []
    for job in scad_jobs(source):
        target = dest / f"{job.stem}.{fmt}"
        openscad(job, target, [])
        written.append(target)
        if preview:
            png = dest / f"{job.stem}.png"
            openscad(
                job,
                png,
                ["--render", "--autocenter", "--viewall", "--imgsize=1024,768", "--colorscheme=Tomorrow"],
            )
            written.append(png)
    return written


def build_py(source: Path, dest: Path) -> list[Path]:
    before = set(dest.iterdir())
    result = subprocess.run(
        ["uv", "run", "--script", str(source), str(dest)], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"{source.relative_to(ROOT)}\n{result.stderr}")
    written = sorted(set(dest.iterdir()) - before)
    if not written:
        raise RuntimeError(f"{source.relative_to(ROOT)} wrote nothing to {dest}")
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("models", nargs="*", help="model slug or path under models/ (default: all)")
    parser.add_argument("--format", choices=["3mf", "stl"], default="3mf")
    parser.add_argument("--no-preview", action="store_true", help="skip PNG previews")
    parser.add_argument(
        "--check", action="store_true", help="render into a temp dir only; fail on any warning"
    )
    args = parser.parse_args()

    if shutil.which("openscad") is None:
        sys.exit("openscad not found on PATH")

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as scratch:
        for source in discover(args.models):
            rel = source.parent.relative_to(MODELS)
            dest = Path(scratch) / rel if args.check else OUT / rel
            dest.mkdir(parents=True, exist_ok=True)
            try:
                if source.suffix == ".scad":
                    written = build_scad(
                        source, dest, args.format, preview=not (args.no_preview or args.check)
                    )
                else:
                    written = build_py(source, dest)
            except RuntimeError as err:
                failures.append(str(err))
                print(f"FAIL {source.relative_to(ROOT)}", file=sys.stderr)
                continue
            for path in written:
                shown = path.relative_to(scratch) if args.check else path.relative_to(ROOT)
                print(f"ok   {shown}")

    if failures:
        print("\n" + "\n\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
