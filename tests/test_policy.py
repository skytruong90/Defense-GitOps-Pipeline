import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import validate_manifests


class PolicyTests(unittest.TestCase):
    def test_repository_manifest_passes(self):
        manifest = Path(__file__).resolve().parents[1] / "manifests" / "app.yaml"
        self.assertEqual(validate_manifests.validate_file(manifest), [])

    def test_mutable_image_is_rejected(self):
        text = (Path(__file__).resolve().parents[1] / "manifests" / "app.yaml").read_text(encoding="utf-8")
        text = text.replace(
            "ghcr.io/example/mission-api@sha256:" + "a" * 64,
            "ghcr.io/example/mission-api:latest",
        )
        violations = validate_manifests.validate_text(text)
        self.assertTrue(any("pinned" in item for item in violations))
        self.assertTrue(any("latest" in item for item in violations))

    def test_privileged_container_is_rejected(self):
        text = (Path(__file__).resolve().parents[1] / "manifests" / "app.yaml").read_text(encoding="utf-8")
        text += "\nprivileged: true\n"
        self.assertTrue(any("privileged" in item for item in validate_manifests.validate_text(text)))


if __name__ == "__main__":
    unittest.main()
