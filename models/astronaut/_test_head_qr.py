"""Regression checks for rigid fit preservation and the raised rear QR."""

import unittest
import io
import numpy as np
import manifold3d as md
from shapely.geometry import box
import trimesh

from head_qr import (HeadSettings, bore_section, mesh_of, relocate_bore,
                     shape_head, solid, visor_rotation, printable_mesh,
                     validate_reference_body, REFERENCE_BOUNDS)


def body_with_bore(y, z, radius=3):
    body = md.Manifold.cube((36, 20, 50)).translate((-18, -10, 0))
    bore = md.Manifold.cylinder(40, radius, circular_segments=128).rotate((0, 90, 0)).translate((-20, y, z))
    return mesh_of(body - bore)


class HeadTests(unittest.TestCase):
    """Check geometry contracts without requiring the private astronaut asset."""

    def test_printed_visor_reference_rejects_a_resized_body(self):
        bounds = np.array(REFERENCE_BOUNDS)
        body = trimesh.creation.box(bounds[1] - bounds[0])
        body.apply_translation(bounds.mean(axis=0))
        validate_reference_body(body)
        body.apply_scale(1.01)
        with self.assertRaisesRegex(ValueError, 'current 50 mm'):
            validate_reference_body(body)

    def test_rotation_is_rigid_and_pocket_faces_down(self):
        body = trimesh.creation.box((24, 20, 24))
        body.apply_transform(trimesh.transformations.rotation_matrix(np.radians(-10), [1, 0, 0]))
        rotation = visor_rotation(body)
        np.testing.assert_allclose(rotation @ rotation.T, np.eye(3), atol=1e-12)
        self.assertAlmostEqual(np.linalg.det(rotation), 1)
        normal = np.array([0, -np.cos(np.radians(10)), np.sin(np.radians(10))])
        np.testing.assert_allclose(rotation @ normal, [0, 0, -1], atol=1e-12)

    def test_relocation_preserves_protected_front_and_size(self):
        original, forward = body_with_bore(2, 42.6), body_with_bore(1, 43)
        rotation = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        result, report = relocate_bore(original, forward, rotation)
        protected = md.Manifold.cube((40, 6, 60)).translate((-20, -10, 0))
        old_region, new_region = solid(original) ^ protected, result ^ protected
        self.assertLess((old_region - new_region).volume(), 1e-7)
        self.assertLess((new_region - old_region).volume(), 1e-7)
        np.testing.assert_allclose(mesh_of(result).bounds, original.bounds)
        np.testing.assert_allclose(bore_section(mesh_of(result)).bounds, bore_section(forward).bounds, atol=1e-6)
        self.assertAlmostEqual(report['bore_forward_mm'], 1)
        self.assertAlmostEqual(report['bore_up_mm'], 0.4)

    def test_relocation_rejects_scaling_and_wrong_direction(self):
        original, forward = body_with_bore(2, 42.6), body_with_bore(1, 43)
        rotation = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        forward.apply_scale(1.01)
        with self.assertRaisesRegex(ValueError, 'original scale'):
            relocate_bore(original, forward, rotation)
        with self.assertRaisesRegex(ValueError, 'forward and upward'):
            relocate_bore(original, body_with_bore(3, 43), rotation)

    def test_bore_diameter_changes_are_rejected(self):
        rotation = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
        with self.assertRaisesRegex(ValueError, 'diameter'):
            relocate_bore(body_with_bore(2, 42.6), body_with_bore(1, 43, radius=2.9), rotation)

    def test_stl_round_trip_discards_only_collapsed_debris(self):
        cube = trimesh.creation.box((10, 10, 10))
        debris = trimesh.Trimesh([[7, 0, 0], [8, 0, 0], [7, 1, 0]],
                                 [[0, 1, 2], [2, 1, 0]], process=False)
        result = printable_mesh(trimesh.util.concatenate([cube, debris]))
        loaded = trimesh.load(io.BytesIO(result.export(file_type='stl')), file_type='stl')
        self.assertTrue(loaded.is_watertight)
        self.assertAlmostEqual(loaded.volume, cube.volume)
        cube.update_faces(np.arange(len(cube.faces) - 2))
        with self.assertRaisesRegex(ValueError, 'physical geometry'):
            printable_mesh(cube)

    def test_cut_is_perpendicular_and_black_is_fully_supported(self):
        source = md.Manifold.cube((24, 30, 18)).translate((-12, -50, -14))
        black, white, report = shape_head(source, np.eye(3), box(0, 0, 33, 33), HeadSettings(module=1, x_limits=None))
        np.testing.assert_allclose(white.bounds, [[0, 0, 0], [24, 25.5, 12.8]])
        np.testing.assert_allclose(black.bounds[:, 2], [12.8, 13])
        self.assertTrue(white.is_watertight)
        self.assertTrue(black.is_watertight)
        neck_faces = np.isclose(white.face_normals[:, 1], 1)
        np.testing.assert_allclose(white.face_normals[neck_faces] @ [0, 0, 1], 0)
        black_footprint = solid(black).slice(12.9)
        self.assertLess((black_footprint - solid(white).slice(12.799)).area(), 1e-7)
        self.assertEqual(report['white_top_z_mm'], 12.8)

    def test_shoulders_are_removed_but_neck_is_retained(self):
        source = md.Manifold.cube((24, 30, 18)).translate((-12, -50, -14))
        shoulder = md.Manifold.cube((30, 5, 8)).translate((-15, -25.8, -10))
        black, white, _ = shape_head(source + shoulder, np.eye(3), box(0, 0, 33, 33),
                                    HeadSettings(module=1, x_limits=None,
                                                 neck_planes=(((1, 0, 0), 12), ((-1, 0, 0), 12))))
        np.testing.assert_allclose(white.extents, [24, 25.5, 12.8])
        self.assertTrue(white.is_watertight)
        self.assertTrue(black.is_watertight)
        with self.assertRaisesRegex(ValueError, 'shoulder cut'):
            shape_head(source, np.eye(3), box(0, 0, 1, 1), HeadSettings(neck_y=-29))

    def test_quiet_zone_must_fit_in_full(self):
        too_narrow = md.Manifold.cube((14, 30, 18)).translate((-7, -50, -14))
        with self.assertRaisesRegex(ValueError, 'quiet zone'):
            shape_head(too_narrow, np.eye(3), box(0, 0, 1, 1), HeadSettings())
        body = md.Manifold.cube((24, 30, 18)).translate((-12, -50, -14))
        with self.assertRaisesRegex(ValueError, 'positive'):
            shape_head(body, np.eye(3), box(0, 0, 1, 1), HeadSettings(depth=0))

    def test_invalid_mesh_and_missing_pocket_fail(self):
        cube = trimesh.creation.box()
        cube.update_faces(np.arange(len(cube.faces) - 1))
        with self.assertRaisesRegex(ValueError, 'closed'):
            solid(cube)
        with self.assertRaisesRegex(ValueError, 'pocket'):
            visor_rotation(trimesh.creation.box())
        with self.assertRaisesRegex(ValueError, '6 mm'):
            bore_section(trimesh.creation.box((36, 20, 50)))


if __name__ == '__main__':
    unittest.main()
