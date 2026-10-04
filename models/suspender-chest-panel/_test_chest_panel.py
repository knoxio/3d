"""Check exported panel dimensions, closed meshes, colour, and invalid parameters."""

from collections import Counter
from pathlib import Path
import subprocess
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('chest_panel.scad')
NS = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}


def _surface_covers(vertices, triangles, point, z):
    for triangle in triangles:
        corners = [vertices[int(triangle.attrib[f'v{i}'])] for i in (1, 2, 3)]
        if any(abs(corner[2] - z) > 0.0001 for corner in corners):
            continue
        a, b, c = corners
        area = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
        if abs(area) < 0.000000001:
            continue
        crosses = [(b[0]-a[0])*(point[1]-a[1]) - (b[1]-a[1])*(point[0]-a[0])
                   for a, b in zip(corners, corners[1:] + corners[:1])]
        if min(crosses) >= -0.000001 or max(crosses) <= 0.000001:
            return True
    return False


class PanelTests(unittest.TestCase):
    """Render real geometry to verify the print contract and parameter guards."""

    def test_print_geometry(self):
        """Each export is closed, correctly positioned, and has the intended thickness."""
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as scratch:
            for part, height, bottom in [('base', 1.2, 0), ('detailing', 0.6, 1.2), ('assembled', 1.8, 0)]:
                with self.subTest(part=part):
                    target = Path(scratch) / f'{part}.3mf'
                    result = subprocess.run(
                        ['openscad', '--hardwarnings', '--backend', 'manifold',
                         '-D', f'part="{part}"', '-o', str(target), str(SOURCE)],
                        capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    with ZipFile(target) as archive:
                        model = ET.fromstring(archive.read('3D/3dmodel.model'))
                    vertices = [tuple(float(v.attrib[a]) for a in 'xyz')
                                for v in model.findall('.//m:vertex', NS)]
                    self.assertTrue(vertices)
                    low = [min(v[a] for v in vertices) for a in range(3)]
                    high = [max(v[a] for v in vertices) for a in range(3)]
                    self.assertAlmostEqual(low[2], bottom, places=5)
                    self.assertAlmostEqual(high[2] - low[2], height, places=5)
                    self.assertGreaterEqual(low[0], -100)
                    self.assertLessEqual(high[0], 100)
                    self.assertGreaterEqual(low[1], -40)
                    self.assertLessEqual(high[1], 40)
                    if part != 'detailing':
                        self.assertAlmostEqual(high[0] - low[0], 200, places=5)
                        self.assertAlmostEqual(high[1] - low[1], 80, delta=0.001)
                    if part == 'base':
                        end_vertices = [v for v in vertices if abs(v[0]) >= 90]
                        self.assertTrue(end_vertices)
                        self.assertLess(max(v[1] for v in end_vertices), 34)
                        self.assertGreater(min(v[1] for v in end_vertices), -33)
                        centre_vertices = [v for v in vertices if abs(v[0]) <= 1]
                        self.assertGreater(max(v[1] for v in centre_vertices), 39)
                        self.assertLess(min(v[1] for v in centre_vertices), -39)
                        top_edge = [v for v in vertices if abs(v[2] - 1.2) < 0.0001]
                        bed_edge = [v for v in vertices if abs(v[2]) < 0.0001]
                        self.assertAlmostEqual(max(v[0] for v in top_edge), 99.5, delta=0.002)
                        self.assertAlmostEqual(max(v[0] for v in bed_edge), 99.8, delta=0.002)
                        round_levels = {round(v[2], 4) for v in vertices if 0.7 < v[2] < 1.2}
                        self.assertGreaterEqual(len(round_levels), 8)
                    triangles = model.findall('.//m:triangle', NS)
                    self.assertTrue(triangles)
                    edges = Counter()
                    for triangle in triangles:
                        indices = [int(triangle.attrib[f'v{i}']) for i in (1, 2, 3)]
                        self.assertEqual(len(set(indices)), 3)
                        for a, b in zip(indices, indices[1:] + indices[:1]):
                            edges[tuple(sorted((a, b)))] += 1
                    self.assertEqual(set(edges.values()), {2})
                    if part == 'detailing':
                        def covers(x, y):
                            point = ((x-100)*166/200, (40-y)*62/80)
                            return _surface_covers(vertices, triangles, point, 1.8)
                        self.assertTrue(covers(108, 13), 'antler branches must join without a pinhole')
                        self.assertTrue(covers(100, 75), 'foliage halves must join without a pinhole')
                        self.assertFalse(covers(116, 25.7), 'eye recess must remain open')
                        self.assertFalse(covers(46, 32), 'outlined leaf must retain its interior opening')
                        self.assertTrue(covers(48, 32.333), 'outlined leaf must retain a printable rim')
                    if part == 'assembled':
                        palette = [b.attrib['displaycolor'] for b in model.findall('.//m:base', NS)]
                        colours = {palette[int(t.attrib['p1'])] for t in triangles}
                        self.assertEqual(colours, {'#000000FF', '#FFFFFFFF'})

    def test_invalid_parameters(self):
        """Reject unsafe thickness, artwork outside the panel, and unknown part names."""
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as scratch:
            for setting in ['base_thickness=0.8', 'panel_width=100', 'relief_height=0.2', 'part="missing"', 'top_curve_rise=-1', 'bottom_curve_drop=80', 'curve_segments=5', 'edge_round_radius=1.1', 'bottom_chamfer=0', 'edge_round_segments=2']:
                with self.subTest(setting=setting):
                    result = subprocess.run(
                        ['openscad', '--hardwarnings', '--backend', 'manifold',
                         '-D', setting, '-o', str(Path(scratch) / 'invalid.3mf'), str(SOURCE)],
                        capture_output=True, text=True,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Assertion', result.stderr)


if __name__ == '__main__':
    unittest.main()
