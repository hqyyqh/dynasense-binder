import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("release", Path(__file__).with_name("check-release.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseCheck(unittest.TestCase):
    def test_snapshot_hold_and_exact_asset_identity(self):
        data = {"id": 4, "published_at": "2026-10-15T00:00:00Z", "assets": [{"id": 5, "name": "dynasense-3.2.1-linux-x64.vsix"}]}
        self.assertIsNone(release.select_asset(data, {"source": "local-snapshot"}))
        policy = {"source": "github-release", "acceptedReleaseId": 3, "acceptedAssetId": 2,
                  "acceptedPublishedAt": "2026-10-14T00:00:00Z"}
        self.assertEqual(release.select_asset(data, policy)["id"], 5)
        with self.assertRaises(ValueError):
            release.select_asset({**data, "published_at": "2026-10-13T00:00:00Z"}, policy)
        policy.update(acceptedReleaseId=4, acceptedAssetId=5)
        self.assertIsNone(release.select_asset(data, policy))
        policy["acceptedAssetId"] = 6
        with self.assertRaises(ValueError):
            release.select_asset(data, policy)
        with self.assertRaises(ValueError):
            release.select_asset({**data, "prerelease": True}, policy)
        with self.assertRaises(ValueError):
            release.select_asset({**data, "assets": data["assets"] * 2}, policy)

    def test_package_identity_platform_and_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "test.vsix"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("extension/package.json", json.dumps({"publisher": "hqyyqh", "name": "dynasense",
                    "version": "3.2.1", "engines": {"vscode": "^1.100.0"}}))
                archive.writestr("extension.vsixmanifest", '<Identity TargetPlatform="linux-x64" />')
            asset = {"name": "dynasense-3.2.1-linux-x64.vsix"}
            digest, version, _ = release.verify_vsix(path, asset)
            self.assertEqual(version, "3.2.1")
            release.verify_vsix(path, {**asset, "digest": "sha256:" + digest})
            with self.assertRaises(ValueError):
                release.verify_vsix(path, {**asset, "digest": "sha256:wrong"})
            with self.assertRaises(ValueError):
                release.verify_vsix(path, {"name": "dynasense-3.2.2-linux-x64.vsix"})


if __name__ == "__main__":
    unittest.main()
