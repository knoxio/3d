# Agent instructions

Shared by Claude Code and Codex (`CLAUDE.md` is a symlink to this file).

This repo holds 3D-printable models requested by the owner. Agents design
them; the owner slices and prints in Bambu Studio. The deliverable for every
request is a printable file in `out/<slug>/` plus the source that produced it.

## Printer

- Printer: **TBD** — build volume TBD. Until set, keep single parts within
  180 × 180 × 180 mm and say so if a design needs more.
- Nozzle 0.4 mm, layer height 0.2 mm, PLA unless the request says otherwise.

## Handling a request

1. Pick a kebab-case slug. Create `models/<slug>/` with a `README.md`
   (template below). If an existing model covers it, extend that instead.
2. Prefer OpenSCAD for anything dimensional or parametric. Use a Python
   generator (`<name>.py`, PEP 723 inline deps, run via `uv run --script`,
   first CLI arg is the output dir) when the shape is procedural, mesh-based,
   or needs a library OpenSCAD lacks (build123d, trimesh, numpy-stl…).
3. Put every tunable dimension in a named top-level variable with a unit
   comment. No magic numbers in geometry.
4. Model in the orientation it prints in: flat face on Z=0, nothing below
   Z=0. Multi-part objects declare `// parts: a b` and a `part` variable.
5. `mise run build <slug>`, then **open the PNG preview(s) and check them** —
   shape, orientation, no missing or floating geometry. Iterate until right.
6. `mise run check` must pass (it fails on any OpenSCAD warning).
7. Report back: the file(s) to open, print settings, and anything the owner
   has to decide or measure.

Ask before guessing a dimension that decides whether the part fits
something real (hole spacing, a phone's thickness, a screw size). State any
dimension you did assume in the model README.

## FDM design rules

- Walls ≥ 1.2 mm (3 perimeters); load-bearing ≥ 2 mm.
- Overhangs ≤ 45° from vertical without supports; bridge ≤ 10 mm.
  Chamfer bottom edges instead of filleting them.
- Clearances: press fit 0.1 mm, sliding fit 0.2–0.3 mm, loose 0.4+ mm per
  side. Holes print undersized — add 0.2 mm to diameter for bolts.
- Horizontal holes > 8 mm: teardrop or flat-topped to avoid support.
- Heat-set inserts (M3): hole 4.0 mm Ø, depth insert + 1 mm.
- Minimum feature ≈ 0.8 mm; minimum embossed text height ≈ 0.6 mm.
- Use `$fn` proportional to size (or `$fa = 1; $fs = 0.4;`), not huge
  global values.

## Model README template

```markdown
# <Name>

<One line: what it is and what it is for.>

## Parameters
| Variable | Default | Meaning |

## Print
Material, layer height, infill, walls, supports (yes/no, where), orientation,
estimated time/filament if known.

## Assumptions
Dimensions that were guessed rather than given or measured.

## Status
draft | printed-ok | needs-changes (with what changed after test prints)
```

## Repo rules

- `out/` and `tmp/` are gitignored; scratch files go in `tmp/`.
- Commit sources, not exports. Only commit a mesh (`.stl`/`.3mf`) when it
  has no source here (downloaded or hand-edited), and note its origin.
- Never commit to `main`. Branch, Conventional Commits, PR.
- Add the model to the table in `README.md`.
