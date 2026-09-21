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

Requires `openscad` (2025+ with the manifold backend) and `uv`.

```bash
make
```

```bash
make MODEL=pcb-cases
```

```bash
make stl
```

```bash
make check
```

Output lands in `out/<slug>/` as `.3mf` (default) or `.stl`, with a `.png`
preview next to each file. Open the `.3mf` in Bambu Studio.

A `// parts: base lid` line in a `.scad` file exports one file per part,
passing `-D part="base"` etc. — the file must declare a top-level `part`
variable and switch on it.

## Models

| Slug | What |
| --- | --- |
| [`pcb-cases`](models/pcb-cases) | Parametric snap-fit cases for bare PCBs |
