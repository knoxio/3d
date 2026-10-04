"""Regression tests for the assembled two-filament chest-panel 3MF."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


SOURCE = Path(__file__).with_name("project.py")
SPEC = importlib.util.spec_from_file_location("chest_panel_project", SOURCE)
assert SPEC is not None and SPEC.loader is not None
project = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project)


def source_mesh(path: Path, z_bottom: float, z_top: float, *, transform: str | None = None) -> None:
    """Write a closed tetrahedral source mesh at a specified print elevation."""
    namespace = project.CORE
    ET.register_namespace("", namespace)
    root = ET.Element(f"{{{namespace}}}model", {"unit": "millimeter"})
    resources = ET.SubElement(root, f"{{{namespace}}}resources")
    obj = ET.SubElement(resources, f"{{{namespace}}}object", {"id": "2", "type": "model"})
    mesh = ET.SubElement(obj, f"{{{namespace}}}mesh")
    vertices = ET.SubElement(mesh, f"{{{namespace}}}vertices")
    for x, y, z in [(-4, -4, z_bottom), (4, -4, z_bottom), (0, 4, z_bottom), (0, 0, z_top)]:
        ET.SubElement(vertices, f"{{{namespace}}}vertex", {"x": str(x), "y": str(y), "z": str(z)})
    triangles = ET.SubElement(mesh, f"{{{namespace}}}triangles")
    for a, b, c in [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]:
        ET.SubElement(triangles, f"{{{namespace}}}triangle", {"v1": str(a), "v2": str(b), "v3": str(c)})
    build = ET.SubElement(root, f"{{{namespace}}}build")
    attributes = {"objectid": "2"}
    if transform is not None:
        attributes["transform"] = transform
    ET.SubElement(build, f"{{{namespace}}}item", attributes)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("3D/3dmodel.model", ET.tostring(root))


class ProjectTests(unittest.TestCase):
    """Check assembly, materials, printer settings, and rejected bad inputs."""

    def setUp(self) -> None:
        self.scratch = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2] / "tmp")
        self.addCleanup(self.scratch.cleanup)
        self.directory = Path(self.scratch.name)
        self.base = self.directory / "chest_panel-base.3mf"
        self.detail = self.directory / "chest_panel-detailing.3mf"
        source_mesh(self.base, 0, 1.2)
        source_mesh(self.detail, 1.2, 1.8)

    def test_assembled_project_has_two_aligned_filaments(self) -> None:
        destination = project.write_project(self.directory)
        with zipfile.ZipFile(destination) as archive:
            model = ET.fromstring(archive.read("3D/3dmodel.model"))
            settings = ET.fromstring(archive.read("Metadata/model_settings.config"))
            profile = json.loads(archive.read("Metadata/project_settings.config"))
        objects = {obj.get("id"): obj for obj in model.findall("{*}resources/{*}object")}
        self.assertEqual(len(objects), 3)
        self.assertEqual([part.get("id") for part in settings.findall("object/part")], ["1", "2"])
        self.assertEqual(
            [part.find("metadata[@key='extruder']").get("value") for part in settings.findall("object/part")],
            ["1", "2"],
        )
        self.assertEqual([component.get("objectid") for component in objects["3"].findall("{*}components/{*}component")], ["1", "2"])
        self.assertEqual(model.find("{*}build/{*}item").get("objectid"), "3")
        for identifier, expected_z in [("1", (0, 1.2)), ("2", (1.2, 1.8))]:
            zs = [float(vertex.get("z")) for vertex in objects[identifier].findall("{*}mesh/{*}vertices/{*}vertex")]
            self.assertEqual((min(zs), max(zs)), expected_z)
        self.assertEqual(profile["filament_colour"], ["#000000", "#FFFFFF"])
        self.assertEqual(profile["filament_diameter"], ["1.75", "1.75"])
        self.assertEqual(profile["flush_volumes_matrix"], ["0", "280", "280", "0"])
        self.assertEqual(profile["nozzle_diameter"], ["0.2"])
        self.assertEqual(profile["layer_height"], "0.1")
        self.assertEqual(profile["wall_loops"], "3")
        self.assertEqual(profile["sparse_infill_density"], "100%")
        self.assertEqual(model.find("{*}metadata[@name='Application']").text, "BambuStudio-02.08.02.61")

    def test_missing_or_misaligned_detail_is_rejected(self) -> None:
        self.detail.unlink()
        with self.assertRaises(FileNotFoundError):
            project.write_project(self.directory)
        source_mesh(self.detail, 0, 0.6)
        with self.assertRaisesRegex(ValueError, "expected Z bounds"):
            project.write_project(self.directory)

    def test_transformed_part_is_rejected(self) -> None:
        source_mesh(self.detail, 1.2, 1.8, transform="1 0 0 0 1 0 0 0 1 5 0 0")
        with self.assertRaisesRegex(ValueError, "transform must be identity"):
            project.write_project(self.directory)


if __name__ == "__main__":
    unittest.main()
