"""Regression tests for rebuilding Python-generated exports in an existing output directory."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('model_build', Path(__file__).with_name('build.py'))
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)
ROOT = Path(__file__).resolve().parents[1]


class PythonExportTests(unittest.TestCase):
    """Accept actual export rewrites and reject generators that produce no output."""

    def test_existing_export_rewritten(self):
        """A second build must return the updated export while omitting untouched files."""
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as scratch:
            destination = Path(scratch)
            export = destination / 'panel.3mf'
            export.write_bytes(b'old mesh')
            untouched = destination / 'preview.png'
            untouched.write_bytes(b'preview')
            def rewrite(*args, **kwargs):
                export.write_bytes(b'updated mesh with new artwork')
                return subprocess.CompletedProcess(args, 0, '', '')
            with patch.object(BUILD.subprocess, 'run', side_effect=rewrite):
                self.assertEqual(BUILD.build_py(ROOT / 'tools/build.py', destination), [export])

    def test_no_output_rejected(self):
        """An unchanged directory still fails rather than falsely reporting a successful export."""
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as scratch:
            destination = Path(scratch)
            (destination / 'panel.3mf').write_bytes(b'unchanged')
            with patch.object(BUILD.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')):
                with self.assertRaisesRegex(RuntimeError, 'wrote nothing'):
                    BUILD.build_py(ROOT / 'tools/build.py', destination)


if __name__ == '__main__':
    unittest.main()
