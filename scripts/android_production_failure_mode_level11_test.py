#!/usr/bin/env python3
"""Level 11: local failure-mode tests for asset provenance audit and QC."""
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PIL import Image
from scripts.android_asset_provenance_audit import audit


class FailureModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.good = self.root / "valid.png"
        img = Image.new("RGB", (128, 128))
        rng = random.Random(11)
        img.putdata([
            (rng.randrange(256), rng.randrange(256), rng.randrange(256))
            for _ in range(128 * 128)
        ])
        img.save(self.good)

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, name, entries):
        path = self.root / name
        path.write_text(json.dumps({"assets": entries}), encoding="utf-8")
        return path

    def entry(self, path=None, source="https://commons.wikimedia.org/wiki/File:Test",
              license="CC BY 4.0"):
        return {"scene": 1, "path": str(path or self.good),
                "source": source, "license": license}

    def test_valid_asset_manifest_passes(self):
        self.assertEqual(audit(self.manifest("valid.json", [self.entry()]), 1)["status"], "PASS")

    def test_missing_asset_is_fail(self):
        result = audit(self.manifest("missing.json", [self.entry(self.root / "absent.png")]), 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["issues"])

    def test_tiny_asset_is_fail(self):
        tiny = self.root / "tiny.png"
        Image.new("RGB", (1, 1)).save(tiny)
        result = audit(self.manifest("tiny.json", [self.entry(tiny)]), 1)
        self.assertEqual(result["status"], "FAIL")

    def test_invalid_image_is_fail(self):
        bad = self.root / "bad.png"
        bad.write_text("not an image", encoding="utf-8")
        result = audit(self.manifest("bad.json", [self.entry(bad)]), 1)
        self.assertEqual(result["status"], "FAIL")

    def test_duplicate_source_degraded(self):
        entries = [self.entry(), dict(self.entry(), scene=2)]
        result = audit(self.manifest("dup.json", entries), 2)
        self.assertEqual(result["status"], "DEGRADED")
        self.assertTrue(any("duplicated source" in item for item in result["degraded"]))

    def test_missing_source_and_license_degraded(self):
        result = audit(self.manifest("degraded.json", [self.entry(source="", license="")]), 1)
        self.assertEqual(result["status"], "DEGRADED")
        self.assertGreaterEqual(len(result["degraded"]), 2)

    def test_external_gate_rejects_degraded(self):
        result = audit(
            self.manifest("external.json", [self.entry(source="fallback graphic", license="generated graphic")]),
            1, require_external=True
        )
        self.assertEqual(result["status"], "FAIL")

    def test_scene_count_mismatch_fail(self):
        result = audit(self.manifest("count.json", [self.entry()]), 2)
        self.assertEqual(result["status"], "FAIL")

    def test_malformed_json_returns_fail_report(self):
        path = self.root / "broken.json"
        path.write_text("{broken", encoding="utf-8")
        result = audit(path, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["issues"])
        self.assertIn("invalid JSON", result["issues"][0])

    def test_nonlist_assets_fails(self):
        path = self.root / "shape.json"
        path.write_text(json.dumps({"assets": None}), encoding="utf-8")
        result = audit(path, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["issues"])

    def test_malformed_source_url_is_reported(self):
        result = audit(self.manifest("url.json", [self.entry(source="https://")]), 1)
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
