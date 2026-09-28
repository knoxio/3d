"""Geometry, SVG parsing and material assignment regressions."""

from pathlib import Path
import tempfile
import io
import unittest
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import Point, box
import trimesh

from build import face_geometry, make_parts, read_artwork, write_plate


class GeometryTests(unittest.TestCase):
    """Exercise manufacturing boundaries with asymmetric synthetic artwork."""

    def test_parts_fill_plate_without_overlap(self):
        """Black and white meet at the face and form an exactly solid card."""
        artwork = box(0, 0, 3, 3).difference(box(1, 1, 2, 2))
        black, white = make_parts(artwork, 10, 1)
        for mesh in (black, white):
            self.assertTrue(mesh.is_watertight)
            self.assertTrue(mesh.is_winding_consistent)
        self.assertAlmostEqual(black.volume + white.volume, 120, places=4)
        overlap = trimesh.boolean.intersection([black, white]).triangles
        signed_volume = np.einsum("ij,ij->i", overlap[:, 0], np.cross(overlap[:, 1], overlap[:, 2])).sum() / 6
        self.assertAlmostEqual(signed_volume, 0, places=6)
        np.testing.assert_allclose(black.bounds[:, 2], [0, 0.2])
        np.testing.assert_allclose(white.bounds, [[0, 0, 0], [10, 10, 1.2]], atol=1e-6)

    def test_diagonally_touching_modules(self):
        """Square QR modules meeting at corners still produce closed parts."""
        artwork = box(0, 0, 1, 1).union(box(1, 1, 2, 2))
        black, white = make_parts(artwork, 10, 1)
        self.assertTrue(black.is_watertight)
        self.assertTrue(white.is_watertight)
        self.assertAlmostEqual(black.volume + white.volume, 120, places=4)

    def test_raised_face_leaves_internal_gaps_and_supported_border(self):
        """Raised mode removes internal white only below the continuous backing."""
        artwork = box(0, 0, 3, 3).difference(box(1, 1, 2, 2))
        black, white = make_parts(artwork, 11, 1, face_height=0.1, raised=True)
        self.assertTrue(black.is_watertight)
        self.assertTrue(white.is_watertight)
        self.assertAlmostEqual(black.volume, 0.8, places=6)
        self.assertAlmostEqual(white.volume, 11 * 11 * 1.1 + (121 - 9) * 0.1, places=6)
        triangles = white.triangles
        bottom = triangles[np.all(np.isclose(triangles[:, :, 2], 0), axis=1)]
        self.assertTrue(len(bottom) > 0)
        self.assertTrue(all(not box(4.001, 4.001, 6.999, 6.999).contains(
            Point(triangle[:, :2].mean(axis=0))) for triangle in bottom))
        recess = triangles[np.all(np.isclose(triangles[:, :, 2], 0.1), axis=1)]
        self.assertTrue(len(recess) > 0)
        np.testing.assert_allclose(black.bounds[:, 2], [0, 0.1])

    def test_quiet_zone_and_face_orientation(self):
        """The SVG's asymmetric mark stays in its original bed-view quadrant."""
        artwork = box(0, 0, 1, 1).union(box(2, 2, 3, 3)).union(box(2, 0, 3, 1))
        face = face_geometry(artwork, 11, 1)
        self.assertEqual(face.bounds, (4, 4, 7, 7))
        self.assertTrue(face.covers(box(6, 4, 7, 5)))
        self.assertFalse(face.intersects(box(4.1, 6.1, 4.9, 6.9)))

    def test_black_up_is_supported_and_not_mirrored(self):
        """Top-facing black sits on a complete base with SVG Y reversed."""
        artwork = box(0, 0, 1, 1).union(box(2, 2, 3, 3)).union(box(2, 0, 3, 1))
        face = face_geometry(artwork, 15, 1)
        for thickness, base_height in [(1.2, 1.0), (0.6, 0.4)]:
            with self.subTest(thickness=thickness):
                black, white = make_parts(artwork, 15, 1, thickness=thickness, black_up=True)
                self.assertTrue(black.is_watertight)
                self.assertTrue(white.is_watertight)
                np.testing.assert_allclose(white.bounds, [[0, 0, 0], [15, 15, base_height]])
                np.testing.assert_allclose(black.bounds[:, 2], [base_height, thickness])
                np.testing.assert_allclose(black.center_mass[:2], [face.centroid.x, 15 - face.centroid.y])
                self.assertAlmostEqual(white.volume, 225 * base_height)
                self.assertAlmostEqual(black.volume, face.area * 0.2, places=6)
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            make_parts(artwork, 15, 1, raised=True, black_up=True)

    def test_stl_clearance_separates_diagonal_contacts(self):
        """A micrometre gap prevents four-face edges after STL coordinate merging."""
        artwork = box(0, 0, 1, 1).union(box(1, 1, 2, 2))
        black, _ = make_parts(artwork, 10, 1, black_up=True, edge_clearance=0.001)
        loaded = trimesh.load(io.BytesIO(black.export(file_type='stl')), file_type='stl')
        self.assertTrue(loaded.is_watertight)
        self.assertEqual(len(loaded.split()), 2)
        for gap in [-0.1, 10]:
            with self.assertRaisesRegex(ValueError, 'clearance'):
                make_parts(artwork, 10, 1, edge_clearance=gap)

    def test_invalid_dimensions_fail(self):
        """Reject degenerate sizes and face layers without backing."""
        for size, module in [(0, 1), (-1, 1), (10, 0)]:
            with self.assertRaises(ValueError):
                face_geometry(box(0, 0, 1, 1), size, module)
        for face, thickness in [(0, 1.2), (1.2, 1.2), (1.3, 1.2)]:
            with self.assertRaises(ValueError):
                make_parts(box(0, 0, 1, 1), 10, 1, face, thickness)
        with self.assertRaises(ValueError):
            face_geometry(box(0, 0, 2, 1), 10, 1)

    def test_svg_holes_rotation_and_unsupported_shapes(self):
        """Even-odd holes survive parsing and unsupported elements fail."""
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / "tmp") as directory:
            source = Path(directory) / "synthetic.svg"
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="clip-path-dot-color"><path d="M0 0H4V4H0Z M1 1H3V3H1Z" clip-rule="evenodd" transform="rotate(90,2,2)"/></clipPath></defs></svg>')
            artwork = read_artwork(source)
            self.assertAlmostEqual(artwork.area, 12)
            self.assertFalse(artwork.intersects(box(1.1, 1.1, 2.9, 2.9)))
            source.write_text('<svg><clipPath id="clip-path-dot-color"><ellipse/></clipPath></svg>')
            with self.assertRaisesRegex(ValueError, "Unsupported SVG element"):
                read_artwork(source)
            source.write_text('<svg/>')
            with self.assertRaisesRegex(ValueError, "clip-path-dot-color"):
                read_artwork(source)

    def test_3mf_materials_and_layout(self):
        """All 18 assemblies retain two assigned parts and bed clearance."""
        black, white = make_parts(box(0, 0, 1, 1), 10, 1)
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1] / "tmp") as directory:
            path = Path(directory) / "test.3mf"
            write_plate(path, [(style, size, black, white) for style in ("A", "B", "C")
                               for size in (10, 12, 15, 20, 25, 30)])
            with zipfile.ZipFile(path) as archive:
                root = ET.fromstring(archive.read("3D/3dmodel.model"))
                settings = ET.fromstring(archive.read("Metadata/model_settings.config"))
            items = root.findall("{*}build/{*}item")
            self.assertEqual(len(items), 18)
            footprints = []
            sizes = (10, 12, 15, 20, 25, 30)
            for index, item in enumerate(items):
                x, y, z = map(float, item.attrib["transform"].split()[-3:])
                self.assertEqual(z, 0)
                size = sizes[index % len(sizes)]
                footprint = box(x, y, x + size, y + size)
                self.assertTrue(box(18, 8, 205, 245).covers(footprint))
                self.assertTrue(all(not footprint.intersects(other) for other in footprints))
                self.assertFalse(footprint.intersects(box(212, 100, 247, 140)))
                footprints.append(footprint)
            for obj in settings.findall("object"):
                self.assertEqual([part.find("metadata[@key='extruder']").attrib["value"]
                                  for part in obj.findall("part")], ["1", "2"])
            with self.assertRaises(ValueError):
                write_plate(path, [])
            with self.assertRaises(ValueError):
                write_plate(path, [("A", 51, black, white)])


if __name__ == "__main__":
    unittest.main()
