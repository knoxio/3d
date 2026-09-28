# Two-colour QR size test

Three designs, each in six sizes (18 separate cards): **10, 12, 15, 20, 25 and 30 mm** square,
including a four-module white quiet zone. Each card is **1.2 mm** thick.
Each original SVG artwork is retained, including its finder rings. Columns A, B
and C are rounded, square and circular dots respectively. Sizes increase from
the front of the bed to the back.

Cards print face down: black inlay and white background occupy Z=0–0.2 mm,
with a continuous white backing at Z=0.2–1.2 mm. With both first-layer and
regular layer heights set to 0.10 mm, this is two mixed-colour layers followed
by ten white layers. Turn the cards over after printing to read them.

The 3MF keeps each card as an assembly with two parts. Assign filament 1 to
black and filament 2 to white. The paired STLs share an origin: import each
pair together as parts of one object, never auto-arrange the two parts apart.

## Generate

Use Python 3.12 or later. Keep the input SVG outside version control: QR
payloads may contain private information. Generated files go in ignored `tmp/`.

```sh
mkdir -p tmp/qr-code
uv venv tmp/qr-code/venv
uv pip install --python tmp/qr-code/venv/bin/python -r qr_code/requirements.txt
tmp/qr-code/venv/bin/python qr_code/build.py /absolute/path/to/rounded.svg /absolute/path/to/square.svg /absolute/path/to/dots.svg --names A-rounded B-square C-dots --output tmp/qr-code/output
PYTHONPYCACHEPREFIX=tmp/qr-code/pycache tmp/qr-code/venv/bin/python -m unittest discover -s qr_code -v
```

The SVG must use `clip-path-dot-color` containing paths, circles and rectangles.
Only rotation transforms and explicit even-odd compound paths are supported.
The default source module pitch is 14 SVG units; change `--module` for another
source. Unsupported geometry is rejected rather than silently omitted.

## Bambu Studio

- Printer: P1S, 0.2 mm nozzle, AMS, black and white PLA.
- Smooth PEI build plate.
- Both initial and regular layer height: 0.10 mm; initial line width: 0.22 mm.
- Arachne walls; elephant-foot compensation: 0 mm, to retain tiny first-layer dots.
- Twelve top and bottom shell layers make these twelve-layer cards solid.
- Initial wall speed: 20 mm/s; initial infill speed: 30 mm/s.
- No support or brim. Prime tower enabled. Do not flush into the white cards.
- Select the actual build plate and filament profiles before printing.

The layout fits within a 256 mm bed and leaves the right side clear for
a 35 mm prime tower at X=212, Y=100. The generated generic 3MF stores geometry and part assignments;
printer/process settings are applied when saving the Bambu Studio project.

For a 33-module QR plus its border, module widths are size/41: 0.244 mm at
10 mm, 0.293 mm at 12 mm and 0.366 mm at 15 mm. The two smallest cards are
experimental with a 0.2 mm nozzle. Digital decoding does not establish physical
scan reliability; compare the actual prints using the intended camera and
lighting. A 1.2 mm solid card is still somewhat flexible, at the larger sizes.

## Raised-face experiment

Add `--raised --sizes 15` to generate a single 15 mm sample. Raised mode uses
one 0.10 mm black layer and a white quiet-zone border on the bed, leaving the
internal gaps empty. Eleven continuous white backing layers follow, preserving
1.2 mm overall thickness. The first backing layer bridges the recessed gaps.

For Bambu Studio, customize the first-layer filament sequence to **1, 2**
(black, then white). Keep 0.10 mm first and regular layer heights, 0.22 mm
first-layer line width, and a 1.00 initial-layer flow multiplier. Keep supports
disabled so they do not fill the intended recess. This is an experiment:
bridging sag and the opacity of a single black layer need physical evaluation.

For a matching dotted face-down sample, supply the dotted SVG with the same
size and relief options; its finder-marker shapes are preserved:

```sh
PYTHONPYCACHEPREFIX=tmp/qr-code/pycache tmp/qr-code/venv/bin/python qr_code/build.py /absolute/path/to/dotted.svg --names Raised-dotted --sizes 15 --raised --output tmp/qr-code/raised-dotted
```

## Black-up experiment

Use `--black-up --sizes 15 --thickness 0.6` with the square-module SVG for a
15 mm card with a 0.4 mm solid white base and a 0.2 mm raised black pattern.
At 0.10 mm layer height, four white layers print first and two black layers
follow. No white is printed alongside the raised black and no gaps need
bridging. The top-facing QR reverses the SVG Y axis to preserve its orientation.
This thinner base is more flexible than the original card.

```sh
PYTHONPYCACHEPREFIX=tmp/qr-code/pycache tmp/qr-code/venv/bin/python qr_code/build.py /absolute/path/to/square.svg --names Black-up-square --sizes 15 --black-up --thickness 0.6 --output tmp/qr-code/black-up
```

Use automatic filament sequencing, keeping filament 1 black and filament 2
white. For this test, use 20 mm/s outer walls, top surfaces and gap infill,
30 mm/s inner walls, and the original 0.22 mm line widths and calibrated flow.
