# 3d

Printable models and the generators that produce them. Sliced and printed in
Bambu Studio.

## Layout

```
models/<slug>/      one directory per object
  README.md         what it is, parameters, print settings, status
  <name>.scad       OpenSCAD source (parametric), and/or
  <name>.py         Python generator (uv script, writes into the dir it is given)
  *.stl / *.3mf     only for non-parametric meshes that have no source here
lib/                shared OpenSCAD modules (`use <../../lib/x.scad>`)
tools/build.py      builds everything under models/ into out/
out/                build output, gitignored
tmp/                scratch, gitignored
```

## Build

Requires `openscad` (2025+ with the manifold backend, `brew install openscad`)
and [mise](https://mise.jdx.dev), which pins `uv`.

```bash
mise run build
```

```bash
mise run build pcb-cases
```

```bash
mise run build -- --format stl
```

```bash
mise run check
```

Output lands in `out/<slug>/` as `.3mf` (default) or `.stl`, with a `.png`
preview next to each file. Open the `.3mf` in Bambu Studio.

A `// parts: base lid` line in a `.scad` file exports one file per part,
passing `-D part="base"` etc. — the file must declare a top-level `part`
variable and switch on it.

A Python generator carrying a `# build: manual` comment is skipped by the
build and by CI, because it needs tools or inputs that are not always there.
Its model README says how to run it.

## Models

| Slug | What |
| --- | --- |
| [`astronaut`](models/astronaut) | Game-asset astronaut turned into a three-part printable keyring (Blender pipeline) |
| [`art-frame`](models/art-frame) | 14-piece dovetailed LED frame for a 1100 × 600 relief tile artwork |
| [`cabinet-light-guide`](models/cabinet-light-guide) | Hidden LED strip channel for a glass cabinet, 3 pieces per 560 mm run |
| [`pcb-cases`](models/pcb-cases) | Parametric snap-fit cases for bare PCBs |
